#!/usr/bin/env python3
"""JANUS 50:50 Cycle-1: JGPT-derived Teacher -> Pivot-Slime-derived Student -> Keymaster.

This is the first matched holdout learning benchmark for the 50:50 corpus.
Scientific boundary:
  * the models see only pre-elimination structural features;
  * local pivot numeric IDs are never model features;
  * exact raw units / safe-vs-overflow / oracle routes are labels only;
  * 24 TRAIN fingerprints are split 18 MODEL_TRAIN + 6 CALIBRATION;
  * 8 HOLDOUT fingerprints remain unseen until final scoring;
  * Keymaster ranking can only order exact checks; exact JANUS decides truth;
  * P_VS_NP remains OPEN.

Lineage notes:
  JGPT teacher is a task-specific derivative of the user's JGPT1.py
  AdaptiveTransformer core: input+position embedding/projection,
  TransformerEncoderLayer, GELU feed-forward, TransformerEncoder, LayerNorm,
  linear head, causal triangular mask.

  Pivot-Slime student is a task-specific derivative of the user's
  MicroGPTSlime: compact attention+MLP residual block with RMSNorm-like
  normalization plus Oxytocin Bond exp(-|gradient|), EMA Slime Trace,
  Piston gradient/loss history, and post-training INT8 quantization audit.

Neither derivative is claimed to be byte-identical to the source model.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import random
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn
import torch.nn.functional as F

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.mad_lab import juxtapose_50x50_multiformula_corpus as corpus_mod

P_VS_NP = "OPEN"
SCHEMA = "JANUS/KEYMASTER/50x50-CYCLE1-JGPT-SLIME/v1.0.0"
DEVICE = torch.device("cpu")
FEATURE_DIM = 7
SEQ_LEN = 7
CANDIDATES = 7


def stable_hash(obj: object) -> str:
    s = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def set_seed(seed: int = 505050) -> None:
    random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(2)


def rmsnorm(x: torch.Tensor, eps: float = 1e-5) -> torch.Tensor:
    return x * torch.rsqrt(x.pow(2).mean(dim=-1, keepdim=True) + eps)


def candidate_tokens(cnf: base.CNF, pivot: int) -> list[list[float]]:
    """Cheap O(n*d) structural tokens available before exact resolution.

    There is no pair enumeration, raw resolvent construction, exact raw unit
    value, safe label, route label or pivot numeric ID in the returned tensor.
    Other variables are sorted by their structural tuple, not numeric name.
    """
    pos = [c for c in cnf if pivot in c]
    neg = [c for c in cnf if -pivot in c]
    retained = [c for c in cnf if pivot not in c and -pivot not in c]
    others = [v for v in base.vars_of(cnf) if v != pivot]
    pairs = max(1, len(pos) * len(neg))
    rows = []
    conflicts = []
    aligneds = []
    overlaps = []
    for v in others:
        pp = sum(v in c for c in pos)
        pm = sum(-v in c for c in pos)
        np = sum(v in c for c in neg)
        nm = sum(-v in c for c in neg)
        conflict = pp * nm + pm * np
        aligned = pp * np + pm * nm
        overlap = (pp + pm) * (np + nm)
        conflicts.append(conflict / pairs)
        aligneds.append(aligned / pairs)
        overlaps.append(overlap / pairs)
        rows.append([
            pp / max(1, len(pos)), pm / max(1, len(pos)),
            np / max(1, len(neg)), nm / max(1, len(neg)),
            conflict / pairs, aligned / pairs, overlap / pairs,
        ])
    rows.sort(key=lambda r: tuple(round(x, 12) for x in r))
    assert len(rows) == 6
    summary = [
        sum(conflicts) / 6.0,
        sum(aligneds) / 6.0,
        sum(overlaps) / 6.0,
        max(conflicts),
        min(conflicts),
        (max(conflicts) - min(conflicts)),
        len(retained) / max(1, len(cnf)),
    ]
    return rows + [summary]


def build_examples(corpus: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for f in corpus["formulas"]:
        cnf = corpus_mod.construct(int(f["seed"]))
        fp = base.fingerprint(cnf)
        assert fp == f["stats"]["fingerprint"]
        raw = [int(f["stress"]["first_pivot"][str(p)]["raw_units"]) for p in range(1, 8)]
        mn, mx = min(raw), max(raw)
        assert f["stress"]["cap"] == mn
        # Current 50:50 stress family deliberately has one safe root pivot.
        best = [i for i, x in enumerate(raw) if x == mn]
        assert len(best) == 1
        tokens = [candidate_tokens(cnf, p) for p in range(1, 8)]
        rel = [(x - mn) / max(1.0, float(mx - mn)) for x in raw]
        out.append({
            "seed": f["seed"], "split": f["split"], "fingerprint": fp,
            "cap": int(f["stress"]["cap"]), "cnf": cnf,
            "tokens": tokens, "raw": raw, "raw_relative": rel,
            "best_index": best[0], "best_pivot_local": best[0] + 1,
            "oracle_champion": f["stress"]["oracle_champion"],
            "exhaustive_exact_checks": int(f["stress"]["exhaustive_exact_checks"]),
            "exhaustive_pair_work": int(f["stress"]["exhaustive_pair_work"]),
        })
    return out


def tensorize(rows: list[dict[str, Any]]) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    x = torch.tensor([r["tokens"] for r in rows], dtype=torch.float32, device=DEVICE)
    y = torch.tensor([r["raw_relative"] for r in rows], dtype=torch.float32, device=DEVICE)
    best = torch.tensor([r["best_index"] for r in rows], dtype=torch.long, device=DEVICE)
    return x, y, best


class JGPTPivotTeacher(nn.Module):
    """Task-specific continuous-feature derivative of JGPT1 AdaptiveTransformer."""
    def __init__(self, d_model: int = 32, nhead: int = 4, layers: int = 2):
        super().__init__()
        self.input_projection = nn.Linear(FEATURE_DIM, d_model)
        self.position_embedding = nn.Embedding(SEQ_LEN, d_model)
        layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, dim_feedforward=4 * d_model,
            dropout=0.0, activation="gelu", batch_first=True,
        )
        self.transformer = nn.TransformerEncoder(layer, num_layers=layers)
        self.ln_f = nn.LayerNorm(d_model)
        self.cost_head = nn.Linear(d_model, 1, bias=False)
        for m in self.modules():
            if isinstance(m, (nn.Linear, nn.Embedding)):
                nn.init.normal_(m.weight, mean=0.0, std=0.02)
                if isinstance(m, nn.Linear) and m.bias is not None:
                    nn.init.zeros_(m.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: B x 7 candidates x 7 sequence tokens x 7 features
        b, c, s, f = x.shape
        z = x.reshape(b * c, s, f)
        pos = torch.arange(s, device=x.device).view(1, s)
        z = self.input_projection(z) + self.position_embedding(pos)
        causal = torch.triu(torch.full((s, s), float("-inf"), device=x.device), diagonal=1)
        z = self.transformer(z, mask=causal)
        z = self.ln_f(z)
        # summary token is deliberately last; causal mask lets it read all prior structural tokens.
        score = self.cost_head(z[:, -1, :]).reshape(b, c)
        return score


class PivotSlimeStudent(nn.Module):
    """Compact task-specific MicroGPTSlime-derived pivot scout."""
    def __init__(self, d_model: int = 16, nhead: int = 2):
        super().__init__()
        self.input_projection = nn.Linear(FEATURE_DIM, d_model)
        self.position_embedding = nn.Parameter(torch.randn(SEQ_LEN, d_model) * 0.02)
        self.attn = nn.MultiheadAttention(d_model, nhead, dropout=0.0, batch_first=True)
        self.fc1 = nn.Linear(d_model, 4 * d_model)
        self.fc2 = nn.Linear(4 * d_model, d_model)
        self.head = nn.Linear(d_model, 1, bias=False)
        self.slime_trace: dict[str, float] = {n: 1.0 for n, _ in self.named_parameters()}
        self.grad_history = deque(maxlen=512)
        self.loss_history = deque(maxlen=512)

    @staticmethod
    def oxytocin_bond(error: float) -> float:
        return math.exp(-max(0.0, float(error)))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        b, c, s, f = x.shape
        z = x.reshape(b * c, s, f)
        z = self.input_projection(z) + self.position_embedding[:s].unsqueeze(0)
        r = z
        q = rmsnorm(z)
        causal = torch.triu(torch.ones(s, s, dtype=torch.bool, device=x.device), diagonal=1)
        a, _ = self.attn(q, q, q, attn_mask=causal, need_weights=False)
        z = r + a
        r = z
        z = rmsnorm(z)
        z = F.relu(self.fc1(z))
        z = self.fc2(z) + r
        score = self.head(rmsnorm(z)[:, -1, :]).reshape(b, c)
        return score

    def slime_step(self, loss: torch.Tensor, lr: float) -> dict[str, float]:
        self.zero_grad(set_to_none=True)
        loss.backward()
        total = 0.0
        bonds = []
        with torch.no_grad():
            for name, p in self.named_parameters():
                if p.grad is None:
                    continue
                p.grad.clamp_(-1.0, 1.0)
                err = float(p.grad.abs().mean().item())
                bond = self.oxytocin_bond(err)
                old = self.slime_trace.get(name, 1.0)
                self.slime_trace[name] = 0.9 * old + 0.1 * bond
                p.add_(p.grad, alpha=-lr * bond)
                total += float(p.grad.pow(2).sum().item())
                bonds.append(bond)
        gnorm = math.sqrt(total)
        self.grad_history.append(gnorm)
        self.loss_history.append(float(loss.item()))
        return {
            "grad_norm": gnorm,
            "mean_oxytocin_bond": sum(bonds) / max(1, len(bonds)),
            "mean_slime_trace": sum(self.slime_trace.values()) / max(1, len(self.slime_trace)),
        }


def loss_components(pred: torch.Tensor, y: torch.Tensor, best: torch.Tensor) -> tuple[torch.Tensor, dict[str, float]]:
    mse = F.mse_loss(pred, y)
    ce = F.cross_entropy(-pred / 0.12, best)
    loss = mse + 0.35 * ce
    return loss, {"mse": float(mse.item()), "listwise_ce": float(ce.item())}


def ranking_metrics(pred: torch.Tensor, rows: list[dict[str, Any]]) -> dict[str, float]:
    p = pred.detach().cpu().tolist()
    top1 = 0
    ranks = []
    regrets = []
    for scores, r in zip(p, rows):
        order = sorted(range(7), key=lambda i: (scores[i], stable_hash(r["tokens"][i]), i))
        rank = order.index(r["best_index"]) + 1
        top1 += int(rank == 1)
        ranks.append(rank)
        regrets.append(r["raw"][order[0]] - min(r["raw"]))
    return {
        "top1_exact_best_recall": top1 / max(1, len(rows)),
        "mean_exact_best_rank": sum(ranks) / max(1, len(ranks)),
        "mean_top1_raw_regret": sum(regrets) / max(1, len(regrets)),
    }


def train_teacher(train_rows: list[dict[str, Any]], calib_rows: list[dict[str, Any]]) -> tuple[JGPTPivotTeacher, dict[str, Any]]:
    model = JGPTPivotTeacher().to(DEVICE)
    opt = torch.optim.AdamW(model.parameters(), lr=0.006, weight_decay=0.002)
    x, y, best = tensorize(train_rows)
    cx, cy, cb = tensorize(calib_rows)
    best_state = copy.deepcopy(model.state_dict())
    best_key = (float("inf"), float("inf"))
    hist = []
    started = time.perf_counter()
    for step in range(501):
        model.train()
        pred = model(x)
        loss, comp = loss_components(pred, y, best)
        opt.zero_grad(set_to_none=True); loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        if step % 25 == 0:
            model.eval()
            with torch.no_grad(): cp = model(cx); closs, _ = loss_components(cp, cy, cb)
            cm = ranking_metrics(cp, calib_rows)
            key = (cm["mean_exact_best_rank"], float(closs.item()))
            hist.append({"step": step, "train_loss": float(loss.item()), "calib_loss": float(closs.item()), **cm, **comp})
            if key < best_key:
                best_key = key; best_state = copy.deepcopy(model.state_dict())
    model.load_state_dict(best_state); model.eval()
    elapsed = time.perf_counter() - started
    with torch.no_grad(): final = ranking_metrics(model(cx), calib_rows)
    return model, {"training_seconds": elapsed, "history": hist, "best_calibration": final, "parameter_count": sum(p.numel() for p in model.parameters())}


def train_student(student_train_rows: list[dict[str, Any]], calib_rows: list[dict[str, Any]], teacher: JGPTPivotTeacher) -> tuple[PivotSlimeStudent, dict[str, Any]]:
    model = PivotSlimeStudent().to(DEVICE)
    x, y, best = tensorize(student_train_rows)
    cx, cy, cb = tensorize(calib_rows)
    teacher.eval()
    with torch.no_grad(): teacher_train = teacher(x); teacher_cal = teacher(cx)
    best_state = copy.deepcopy(model.state_dict()); best_trace = copy.deepcopy(model.slime_trace)
    best_key = (float("inf"), float("inf")); hist = []
    started = time.perf_counter()
    for step in range(701):
        model.train(); pred = model(x)
        exact_loss, comp = loss_components(pred, y, best)
        distill = F.mse_loss(pred, teacher_train)
        loss = 0.65 * exact_loss + 0.35 * distill
        slime = model.slime_step(loss, lr=0.015)
        if step % 25 == 0:
            model.eval()
            with torch.no_grad(): cp = model(cx); cl_exact, _ = loss_components(cp, cy, cb); cl_dist = F.mse_loss(cp, teacher_cal); closs = 0.65 * cl_exact + 0.35 * cl_dist
            cm = ranking_metrics(cp, calib_rows)
            key = (cm["mean_exact_best_rank"], float(closs.item()))
            hist.append({"step": step, "train_loss": float(loss.item()), "calib_loss": float(closs.item()), "distill_loss": float(distill.item()), **cm, **comp, **slime})
            if key < best_key:
                best_key = key; best_state = copy.deepcopy(model.state_dict()); best_trace = copy.deepcopy(model.slime_trace)
    model.load_state_dict(best_state); model.slime_trace = best_trace; model.eval()
    elapsed = time.perf_counter() - started
    with torch.no_grad(): final = ranking_metrics(model(cx), calib_rows)
    return model, {"training_seconds": elapsed, "history": hist, "best_calibration": final, "parameter_count": sum(p.numel() for p in model.parameters()), "mean_slime_trace": sum(model.slime_trace.values()) / max(1, len(model.slime_trace)), "piston_grad_samples": len(model.grad_history), "piston_loss_samples": len(model.loss_history)}


def quantize_int8_inplace(model: nn.Module) -> dict[str, Any]:
    audit = {}
    with torch.no_grad():
        for name, p in model.named_parameters():
            if not p.is_floating_point() or p.numel() == 0:
                continue
            ma = float(p.abs().max().item())
            scale = ma / 127.0 if ma > 0 else 1.0
            q = torch.clamp(torch.round(p / scale), -127, 127)
            deq = q * scale
            err = float((deq - p).abs().max().item())
            p.copy_(deq)
            audit[name] = {"scale": scale, "max_abs_error": err}
    return {"scheme": "SYMMETRIC_INT8_DEQUANTIZED_FOR_EXACT_SAME_RUNTIME_API", "tensors": audit, "tensor_count": len(audit)}


def flat_feature(row: dict[str, Any], candidate_index: int) -> list[float]:
    return [x for tok in row["tokens"][candidate_index] for x in tok]


def m2r_scores(train_rows: list[dict[str, Any]], target: dict[str, Any], k: int = 7) -> list[float]:
    memory = []
    for r in train_rows:
        for i in range(7): memory.append((flat_feature(r, i), float(r["raw_relative"][i])))
    out = []
    for i in range(7):
        v = flat_feature(target, i)
        ds = []
        for u, y in memory:
            d = math.sqrt(sum((a - b) ** 2 for a, b in zip(v, u)))
            ds.append((d, y))
        nearest = sorted(ds, key=lambda z: z[0])[:k]
        num = sum(y / max(1e-6, d) for d, y in nearest)
        den = sum(1.0 / max(1e-6, d) for d, _ in nearest)
        out.append(num / den)
    return out


def rank_from_scores(scores: list[float], row: dict[str, Any]) -> list[int]:
    return sorted(range(7), key=lambda i: (float(scores[i]), stable_hash(row["tokens"][i]), i))


def exact_runtime_policy(row: dict[str, Any], candidate_order_indices: list[int]) -> dict[str, Any]:
    root = row["cnf"]; cap = row["cap"]
    checks = 0; pair_work = 0; raw_sum = 0; peak_raw = base.state_units(root)
    attempted = []; safe_pivot = None; state = None
    for idx in candidate_order_indices:
        p = idx + 1; checks += 1
        out, st = base.eliminate_var_capped(root, p, cap)
        raw = int(st["raw_units"]); pairs = int(st.get("pairs", 0))
        pair_work += pairs; raw_sum += raw; peak_raw = max(peak_raw, raw)
        attempted.append({"pivot_local": p, "raw_units": raw, "pairs": pairs, "fit": out is not None})
        if out is not None:
            assert base.verify_elimination_transition(root, p, out, cap)
            safe_pivot = p; state = out; break
    if state is None:
        raise AssertionError("ranking exhausted without safe first pivot")
    # Fixed continuation, identical policy for every benchmark after the first safe root action.
    continuation = [p for p in range(1, 8) if p != safe_pivot]
    for p in continuation:
        if state == ((),): break
        if p not in set(base.vars_of(state)): continue
        checks += 1
        out, st = base.eliminate_var_capped(state, p, cap)
        raw = int(st["raw_units"]); pairs = int(st.get("pairs", 0))
        pair_work += pairs; raw_sum += raw; peak_raw = max(peak_raw, raw)
        if out is None:
            raise AssertionError("fixed continuation overflowed after exact-safe first pivot; corpus assumption changed")
        assert base.verify_elimination_transition(state, p, out, cap)
        state = out
    assert state == ((),)
    return {"terminal_unsat": True, "exact_checks_attempted": checks, "pair_work": pair_work, "raw_units_sum": raw_sum, "peak_raw_units": peak_raw, "safe_first_pivot_local": safe_pivot, "root_attempts": attempted, "terminal_depth": 7}


def attention_edges(train_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    # Coarse structural buckets are deliberately advisory. They are built only
    # from TRAIN/CALIB exact labels and never from HOLDOUT.
    buckets: dict[tuple[int, int, int], dict[str, Any]] = {}
    for r in train_rows:
        for i in range(7):
            summary = r["tokens"][i][-1]
            key = tuple(int(round(summary[j] * 40)) for j in range(3))
            b = buckets.setdefault(key, {"safe": 0, "total": 0, "fps": set()})
            b["total"] += 1; b["safe"] += int(i == r["best_index"]); b["fps"].add(r["fingerprint"])
    edges = []
    for key, b in sorted(buckets.items()):
        safe_rate = b["safe"] / b["total"]
        pattern = "pattern:" + "-".join(map(str, key))
        target = "outcome:SAFE_FIRST" if safe_rate >= (1 / 7) else "outcome:OVERFLOW_FIRST"
        ek = f"{pattern}|{target}|EXACT_TRAIN_ASSOCIATION|"
        edges.append({
            "edge_key": ek, "source": pattern, "target": target,
            "relation": "EXACT_TRAIN_ASSOCIATION", "weight": round(0.18 + 0.45 * abs(safe_rate - 1 / 7), 6),
            "observed_this_pass": True, "fresh_evidence_signature": True,
            "evidence_count": b["total"], "independence_count": len(b["fps"]),
            "contradiction_count": min(b["safe"], b["total"] - b["safe"]),
            "status": "TRAIN_ONLY_STRUCTURAL_ASSOCIATION",
            "claim_authority": "DISCOVERY_PRIORITY_ONLY__NOT_CAUSATION_OR_PROOF",
        })
    return edges


def evaluate_model_scores(model: nn.Module, rows: list[dict[str, Any]]) -> list[list[float]]:
    x, _, _ = tensorize(rows)
    model.eval()
    with torch.no_grad(): return model(x).cpu().tolist()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--json-out", type=Path, required=True)
    ap.add_argument("--spider-edge-out", type=Path, required=True)
    args = ap.parse_args()
    set_seed()
    corpus = json.loads(args.corpus.read_text(encoding="utf-8"))
    assert corpus["P_VS_NP"] == "OPEN"
    assert corpus["selection"]["train_formulas"] == 24 and corpus["selection"]["holdout_formulas"] == 8
    examples = build_examples(corpus)
    train24 = [r for r in examples if r["split"] == "TRAIN"]
    holdout = [r for r in examples if r["split"] == "HOLDOUT"]
    model_train = train24[:18]; calib = train24[18:]
    assert len(model_train) == 18 and len(calib) == 6 and len(holdout) == 8

    teacher, teacher_audit = train_teacher(model_train, calib)
    student, student_audit = train_student(model_train, calib, teacher)
    teacher_hold = evaluate_model_scores(teacher, holdout)
    student_float_hold = evaluate_model_scores(student, holdout)
    float_student_metrics = ranking_metrics(torch.tensor(student_float_hold), holdout)
    q_audit = quantize_int8_inplace(student)
    student_hold = evaluate_model_scores(student, holdout)
    quant_student_metrics = ranking_metrics(torch.tensor(student_hold), holdout)

    teacher_metrics = ranking_metrics(torch.tensor(teacher_hold), holdout)
    m2r_all = [m2r_scores(train24, r) for r in holdout]
    m2r_metrics = ranking_metrics(torch.tensor(m2r_all), holdout)

    policies = defaultdict(list)
    per_formula = []
    for j, r in enumerate(holdout):
        teacher_s = teacher_hold[j]; student_s = student_hold[j]; m2r_s = m2r_all[j]
        fused = [0.50 * teacher_s[i] + 0.30 * student_s[i] + 0.20 * m2r_s[i] for i in range(7)]
        orders = {
            "STATIC_NUMERIC_NEGATIVE_CONTROL": list(range(7)),
            "M2R_PM_ONLY": rank_from_scores(m2r_s, r),
            "JGPT_TEACHER": rank_from_scores(teacher_s, r),
            "PIVOT_SLIME_INT8": rank_from_scores(student_s, r),
            "KEYMASTER_FUSED": rank_from_scores(fused, r),
            "ORACLE_LOWER_BOUND": [r["best_index"]] + [i for i in range(7) if i != r["best_index"]],
        }
        rec = {"fingerprint": r["fingerprint"], "seed": r["seed"], "best_pivot_local": r["best_pivot_local"], "cap": r["cap"], "policies": {}}
        for name, order in orders.items():
            rt = exact_runtime_policy(r, order)
            rank = order.index(r["best_index"]) + 1
            item = {"ranking_local_for_audit_only": [i + 1 for i in order], "exact_best_rank": rank, "top1_hit": rank == 1, "runtime": rt}
            rec["policies"][name] = item; policies[name].append(item)
        per_formula.append(rec)

    aggregate = {}
    for name, vals in policies.items():
        aggregate[name] = {
            "holdout_formulas": len(vals),
            "top1_exact_best_recall": sum(int(v["top1_hit"]) for v in vals) / len(vals),
            "mean_exact_best_rank": sum(v["exact_best_rank"] for v in vals) / len(vals),
            "exact_checks_attempted": sum(v["runtime"]["exact_checks_attempted"] for v in vals),
            "pair_work": sum(v["runtime"]["pair_work"] for v in vals),
            "raw_units_sum": sum(v["runtime"]["raw_units_sum"] for v in vals),
            "peak_raw_units_max": max(v["runtime"]["peak_raw_units"] for v in vals),
            "terminal_unsat_count": sum(int(v["runtime"]["terminal_unsat"]) for v in vals),
        }

    b = aggregate["STATIC_NUMERIC_NEGATIVE_CONTROL"]; k = aggregate["KEYMASTER_FUSED"]
    delta = {
        "baseline": "STATIC_NUMERIC_NEGATIVE_CONTROL",
        "scope": "8_FINGERPRINT_HOLDOUT__50x50_ROOT_GATE",
        "exact_checks_saved": b["exact_checks_attempted"] - k["exact_checks_attempted"],
        "exact_checks_saved_fraction": (b["exact_checks_attempted"] - k["exact_checks_attempted"]) / max(1, b["exact_checks_attempted"]),
        "exact_check_capacity_multiplier": b["exact_checks_attempted"] / max(1, k["exact_checks_attempted"]),
        "pair_work_saved": b["pair_work"] - k["pair_work"],
        "pair_work_saved_fraction": (b["pair_work"] - k["pair_work"]) / max(1, b["pair_work"]),
        "pair_work_capacity_multiplier": b["pair_work"] / max(1, k["pair_work"]),
    }
    training_data_pair_work = sum(r["exhaustive_pair_work"] for r in train24)
    training_data_checks = sum(r["exhaustive_exact_checks"] for r in train24)
    delta["training_data_generation_pair_work"] = training_data_pair_work
    delta["training_data_generation_exact_checks"] = training_data_checks
    delta["net_pair_work_after_charging_cycle0_data_generation"] = delta["pair_work_saved"] - training_data_pair_work
    delta["resource_positive_on_first_8_holdout_horizon"] = delta["net_pair_work_after_charging_cycle0_data_generation"] > 0

    edges = attention_edges(train24)
    args.spider_edge_out.parent.mkdir(parents=True, exist_ok=True)
    args.spider_edge_out.write_text("".join(json.dumps(e, sort_keys=True, separators=(",", ":")) + "\n" for e in edges), encoding="utf-8")

    payload = {
        "schema": SCHEMA,
        "status": "CYCLE1_HOLDOUT_MEASURED__ADVISORY_LEARNING_ONLY",
        "P_VS_NP": P_VS_NP,
        "lineage": {
            "teacher": "TASK_SPECIFIC_DERIVATIVE_OF_JGPT1_ADAPTIVE_TRANSFORMER__NOT_BYTE_IDENTICAL",
            "student": "TASK_SPECIFIC_DERIVATIVE_OF_MICROGPTSLIME__NOT_BYTE_IDENTICAL",
            "teacher_core_preserved": ["continuous input projection analogous to embedding", "position embedding", "TransformerEncoderLayer", "GELU", "TransformerEncoder", "LayerNorm", "linear head", "causal triangular mask"],
            "student_core_preserved": ["attention residual block", "RMSNorm-like normalization", "Oxytocin Bond exp(-error)", "EMA Slime Trace", "Piston grad/loss history", "INT8 quantization audit"],
        },
        "split": {"model_train": 18, "calibration": 6, "holdout": 8, "by_formula_fingerprint": True},
        "feature_firewall": {
            "pivot_numeric_id_in_model_input": False,
            "exact_raw_units_in_model_input": False,
            "oracle_route_in_model_input": False,
            "safe_overflow_label_in_model_input": False,
            "feature_computation": "O(n*d) parent sign/cooccurrence counts only; no resolvent pair enumeration",
            "other_variables_sorted_by_structure_not_numeric_id": True,
        },
        "teacher_audit": teacher_audit,
        "student_audit": student_audit,
        "student_float_holdout": float_student_metrics,
        "student_int8_holdout": quant_student_metrics,
        "student_int8_quantization": q_audit,
        "direct_holdout_prediction_metrics": {"JGPT_TEACHER": teacher_metrics, "M2R_PM_ONLY": m2r_metrics},
        "keymaster_fusion": {"weights_preregistered_before_holdout": {"JGPT_TEACHER": 0.50, "PIVOT_SLIME_INT8": 0.30, "M2R_PM": 0.20}, "TOPA_SPIDER_ATTENTION_IN_CURRENT_RANKING": False, "reason": "First 50x50 cycle has no prior 50x50 PIPPI/Spider attention history; train-only Spider ecology is generated after scoring for the next mirror/cycle."},
        "aggregate_exact_runtime": aggregate,
        "PIPPI_DELTA1": delta,
        "per_holdout_formula": per_formula,
        "spider_train_relation_edges": len(edges),
        "scientific_firewall": {
            "MODEL_PREDICTION_IS_NOT_PROOF": True,
            "KEYMASTER_ONLY_REORDERS_EXACT_CHECKS": True,
            "HOLDOUT_WAS_NOT_USED_FOR_TRAINING_OR_ATTENTION_BUILD": True,
            "SPIDER_EDGE_IS_NOT_CAUSATION": True,
            "ATTENTION_WEIGHT_IS_NOT_EVIDENCE_WEIGHT": True,
            "STATIC_NUMERIC_BASELINE_IS_A_NEGATIVE_CONTROL_NOT_A_UNIVERSAL_BASELINE": True,
            "FIRST_CYCLE_RESOURCE_POSITIVITY_MUST_CHARGE_DATA_GENERATION": True,
            "P_VS_NP": P_VS_NP,
        },
    }
    payload["sha256"] = stable_hash(payload)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "teacher_holdout": teacher_metrics,
        "slime_int8_holdout": quant_student_metrics,
        "keymaster": aggregate["KEYMASTER_FUSED"],
        "static": aggregate["STATIC_NUMERIC_NEGATIVE_CONTROL"],
        "PIPPI_DELTA1": delta,
        "spider_edges": len(edges),
        "P_VS_NP": P_VS_NP,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
