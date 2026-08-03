#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from janus_c047_affine_trellis_core import *

SCHEMA_C048 = "janus.c048.proof_carrying_affine_layout_selector.v1"
OPEN_PORTFOLIO_EXHAUSTED = "OPEN_PORTFOLIO_EXHAUSTED"
OPEN_DISCOVERY_BUDGET = "OPEN_DISCOVERY_BUDGET"
MAX_LAYOUT_CANDIDATES = 8
DISCOVERY_MULTIPLIER = 128
DISCOVERY_EXPONENT = 5
SELECTOR_CERT_MULTIPLIER = 128
SELECTOR_CERT_EXPONENT = 7


def normal_space(factor: dict[str, Any]) -> LinearSpace:
    return tuple(mask for mask, _ in factor["equations"])


def layout_data(
    normalized: list[dict[str, Any]],
    order: list[int],
    dimension: int,
) -> dict[str, Any]:
    if sorted(order) != list(range(len(normalized))):
        raise ValueError("order is not a permutation")
    ordered = [normalized[i] for i in order]
    prefix: list[LinearSpace] = [()]
    for factor in ordered:
        prefix.append(span(prefix[-1], normal_space(factor), dimension=dimension))
    suffix: list[LinearSpace] = [() for _ in range(len(ordered) + 1)]
    for i in range(len(ordered) - 1, -1, -1):
        suffix[i] = span(normal_space(ordered[i]), suffix[i + 1], dimension=dimension)
    boundaries: list[LinearSpace] = []
    widths: list[int] = []
    for i in range(len(ordered) + 1):
        boundary = intersection(prefix[i], suffix[i], dimension)
        boundaries.append(boundary)
        widths.append(len(boundary))
    return {
        "order_positions": list(order),
        "factor_order": [factor["factor_id"] for factor in ordered],
        "input_positions": [factor["input_position"] for factor in ordered],
        "cut_widths": widths,
        "max_cut_width": max(widths, default=0),
        "total_cut_width": sum(widths),
        "boundaries": [list(boundary) for boundary in boundaries],
    }


@dataclass
class DiscoveryMeter:
    limit: int
    work: int = 0
    candidate_tests: int = 0
    rank_work: int = 0

    def charge(self, stage: str, amount: int = 1) -> None:
        attempted = self.work + max(1, int(amount))
        if attempted > self.limit:
            raise OpenResult(
                OPEN_DISCOVERY_BUDGET,
                stage,
                {"attempted_discovery_work": attempted, "discovery_limit": self.limit},
            )
        self.work = attempted

    def snapshot(self) -> dict[str, int]:
        return {
            "total_discovery_work": self.work,
            "candidate_tests": self.candidate_tests,
            "rank_work": self.rank_work,
        }


def discovery_limit(input_size: int, cap: int | None = None) -> int:
    polynomial = DISCOVERY_MULTIPLIER * (input_size + 1) ** DISCOVERY_EXPONENT
    return min(polynomial, cap if cap is not None else polynomial)


def selector_certificate_limit(input_size: int, cap: int | None = None) -> int:
    polynomial = SELECTOR_CERT_MULTIPLIER * (input_size + 1) ** SELECTOR_CERT_EXPONENT
    return min(polynomial, cap if cap is not None else polynomial)


def greedy_min_frontier_order(
    normalized: list[dict[str, Any]],
    dimension: int,
    meter: DiscoveryMeter,
) -> list[int]:
    remaining = list(range(len(normalized)))
    prefix: LinearSpace = ()
    order: list[int] = []
    while remaining:
        best: tuple[Any, int, LinearSpace] | None = None
        for candidate in remaining:
            meter.candidate_tests += 1
            meter.charge("greedy_candidate")
            candidate_prefix = span(prefix, normal_space(normalized[candidate]), dimension=dimension)
            remaining_span = span(
                *(normal_space(normalized[index]) for index in remaining if index != candidate),
                dimension=dimension,
            )
            frontier = intersection(candidate_prefix, remaining_span, dimension)
            meter.rank_work += len(candidate_prefix) + len(remaining_span)
            meter.charge("greedy_rank_work", max(1, len(candidate_prefix) + len(remaining_span)))
            factor = normalized[candidate]
            key = (
                len(frontier),
                len(candidate_prefix),
                len(normal_space(factor)),
                normal_space(factor),
                tuple(rhs for _, rhs in factor["equations"]),
                factor["factor_id"],
                factor["input_position"],
            )
            if best is None or key < best[0]:
                best = (key, candidate, candidate_prefix)
        assert best is not None
        _, chosen, prefix = best
        order.append(chosen)
        remaining.remove(chosen)
    return order


def greedy_max_overlap_order(
    normalized: list[dict[str, Any]],
    dimension: int,
    meter: DiscoveryMeter,
) -> list[int]:
    remaining = list(range(len(normalized)))
    prefix: LinearSpace = ()
    order: list[int] = []
    while remaining:
        scored: list[tuple[Any, int, LinearSpace]] = []
        for candidate in remaining:
            meter.candidate_tests += 1
            meter.charge("overlap_candidate")
            space = normal_space(normalized[candidate])
            overlap = intersection(prefix, space, dimension)
            candidate_prefix = span(prefix, space, dimension=dimension)
            remaining_span = span(
                *(normal_space(normalized[index]) for index in remaining if index != candidate),
                dimension=dimension,
            )
            frontier = intersection(candidate_prefix, remaining_span, dimension)
            meter.rank_work += len(prefix) + len(space) + len(remaining_span)
            meter.charge("overlap_rank_work", max(1, len(prefix) + len(space) + len(remaining_span)))
            factor = normalized[candidate]
            key = (
                -len(overlap),
                len(frontier),
                len(candidate_prefix),
                space,
                factor["factor_id"],
                factor["input_position"],
            )
            scored.append((key, candidate, candidate_prefix))
        scored.sort(key=lambda item: item[0])
        _, chosen, prefix = scored[0]
        order.append(chosen)
        remaining.remove(chosen)
    return order


def generate_candidate_manifest(
    factors: list[dict[str, Any]],
    dimension: int,
    *,
    discovery_cap: int | None = None,
) -> dict[str, Any]:
    normalized = normalize_factors(factors, dimension)
    L = input_length(normalized, dimension)
    meter = DiscoveryMeter(discovery_limit(L, discovery_cap))
    try:
        meter.charge("normalize", max(1, len(normalized)))
        base = deterministic_order(normalized)
        constructors: list[tuple[str, list[int]]] = [
            ("PARALLEL_BLOCKS_FIRST_OCCURRENCE", base),
            ("REVERSE_PARALLEL_BLOCKS", list(reversed(base))),
            ("GREEDY_MIN_FRONTIER", greedy_min_frontier_order(normalized, dimension, meter)),
            ("GREEDY_MAX_PREFIX_OVERLAP", greedy_max_overlap_order(normalized, dimension, meter)),
        ]
        candidates: list[dict[str, Any]] = []
        seen: dict[tuple[int, ...], int] = {}
        for constructor, order in constructors:
            meter.charge("candidate_finalize", max(1, len(order)))
            key = tuple(order)
            if key in seen:
                candidates[seen[key]]["aliases"].append(constructor)
                continue
            if len(candidates) >= MAX_LAYOUT_CANDIDATES:
                raise OpenResult(
                    OPEN_DISCOVERY_BUDGET,
                    "candidate_count",
                    {"attempted_candidates": len(candidates) + 1, "candidate_limit": MAX_LAYOUT_CANDIDATES},
                )
            data = layout_data(normalized, order, dimension)
            candidate = {
                "candidate_id": len(candidates),
                "constructor": constructor,
                "aliases": [],
                **data,
            }
            candidate["layout_digest"] = digest(candidate)
            seen[key] = len(candidates)
            candidates.append(candidate)
        manifest = {
            "normalized_input_digest": digest(
                {
                    "dimension": dimension,
                    "factors": [
                        {
                            "factor_id": factor["factor_id"],
                            "equations": [list(eq) for eq in factor["equations"]],
                            "input_position": factor["input_position"],
                        }
                        for factor in normalized
                    ],
                }
            ),
            "constructors_frozen_before_probes": [name for name, _ in constructors],
            "unique_candidates": candidates,
            "candidate_count": len(candidates),
            "discovery_ledger": meter.snapshot(),
        }
        manifest["manifest_digest"] = digest(manifest)
        return {"status": "MANIFEST_FROZEN", "manifest": manifest}
    except OpenResult as err:
        return {
            "status": err.status,
            "reason": err.stage,
            "overflow_evidence": err.evidence,
            "discovery_ledger": meter.snapshot(),
        }
