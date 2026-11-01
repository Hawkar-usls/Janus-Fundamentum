#!/usr/bin/env python3
"""TIME-SAT-004B — bounded HTTPS acquisition and strict streaming DIMACS screening.

Only the EXACT 12 pre-registered external-origin GBD identifiers are eligible.
The 32-character GBD database ID is not a SHA256. We calculate SHA256 of
the ORIGINAL TRANSFER BYTES and of the decoded CNF separately. No conversion
is passed as an externally verified original. Failure remains explicit.
Limits protect GitHub Actions from bandwidth/CPU/RAM/decompression bombs.

Scientific claims: public-origin feasibility ONLY; no hidden-test, solver
speedup, third-party witness, or portable UNSAT certificate in this step.
"""
from __future__ import annotations
import argparse
import bz2
import gzip
from hashlib import sha256
import io
import json
import lzma
import os
from pathlib import Path
import re
import ssl
import sys
from time import monotonic
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener, HTTPSHandler

PRE_REG="experiments/time_sat_004_external/PREREGISTERED_SATCOMP2026_PILOT_20261101.json"
GIT_BLOB_SHA="dc658d57453813bb306aa20f45b3385571f1fe3d"
MAX_TRANSFER_BYTES=52_428_800
MAX_DECOMPRESSED_BYTES=134_217_728
MAX_PER_REQUEST_SECONDS=15
MAX_VARS_PARSE=5_000_000
MAX_CLAUSES_PARSE=8_000_000
MAX_LITERALS_PARSE=100_000_000
MAX_CLAUSE_WIDTH_PARSE=200_000
MAX_VARS_SOLVE=300_000
MAX_CLAUSES_SOLVE=300_000
MAX_LITERALS_SOLVE=2_000_000
SHA_RE=re.compile(r"^[0-9a-f]{32}$")


class BoundedFailure(Exception):
    def __init__(self,reason):
        super().__init__(reason)
        self.reason=reason


class HostConstrainedRedirects(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        target=urlparse(newurl)
        if (target.scheme!="https" or target.hostname!="benchmark-database.de"
                or target.username or target.password):
            raise BoundedFailure("UNTRUSTED_DOWNLOAD_REDIRECT")
        return super().redirect_request(req,fp,code,msg,headers,newurl)


def trusted_uri(candidate):
    digest=candidate.get("hash","")
    uri=candidate.get("official_uri","")
    if not SHA_RE.fullmatch(digest):
        raise BoundedFailure("INVALID_OFFICIAL_HASH_ID")
    p=urlparse(uri)
    if (p.scheme not in ("http","https") or p.hostname!="benchmark-database.de"
            or p.username or p.password or p.port is not None
            or p.path!="/file/"+digest or p.query or p.fragment):
        raise BoundedFailure("OFFICIAL_URI_MISMATCH")
    return "https://benchmark-database.de/file/"+digest


def retrieve(candidate, folder, *, limit=MAX_TRANSFER_BYTES):
    """Stream transfer in strict capped chunks. Never send to an arbitrary URL."""
    url=trusted_uri(candidate)
    request=Request(url,headers={"User-Agent":"JANUS-Research-004B/1.0 (bounded original source screening)","Accept":"application/octet-stream,*/*"})
    opener=build_opener(HTTPSHandler(context=ssl.create_default_context()),
                       HostConstrainedRedirects())
    target=folder/(candidate["hash"]+".download")
    began=monotonic()
    count=0
    h=sha256()
    try:
        with opener.open(request,timeout=6) as resp, target.open("wb") as out:
            if urlparse(resp.url).hostname!="benchmark-database.de" or urlparse(resp.url).scheme!="https":
                raise BoundedFailure("FINAL_DOWNLOAD_ORIGIN_UNTRUSTED")
            declared=resp.headers.get("Content-Length")
            if declared is not None and int(declared)>limit:
                raise BoundedFailure("SOURCE_CONTENT_LENGTH_EXCEEDS_LIMIT")
            while True:
                if monotonic()-began>MAX_PER_REQUEST_SECONDS:
                    raise BoundedFailure("SOURCE_FETCH_TIME_BUDGET")
                data=resp.read(min(64*1024,limit-count+1))
                if not data: break
                count+=len(data)
                if count>limit:raise BoundedFailure("SOURCE_BYTES_EXCEED_LIMIT")
                h.update(data)
                out.write(data)
    except Exception:
        target.unlink(missing_ok=True)
        raise
    return target,{"source_url":url,"source_sha256":h.hexdigest(),
                   "original_transfer_bytes":count,
                   "source_header_content_type":resp.headers.get("Content-Type"),
                   "source_kind":"ORIGINAL_GBD_TRANSFER_NOT_PREVIOUSLY_SHA_PINNED"}


def unpack_bounded(original:Path,dest:Path,*,limit=MAX_DECOMPRESSED_BYTES):
    """Supported original xz/gzip/bzip2/raw without external shell commands."""
    with original.open("rb") as src:
        prefix=src.read(8)
    if prefix.startswith(b"\xfd7zXZ\x00"):kind="xz";opener=lzma.open
    elif prefix.startswith(b"\x1f\x8b"):kind="gzip";opener=gzip.open
    elif prefix.startswith(b"BZh"):kind="bzip2";opener=bz2.open
    else:kind="raw";opener=open
    size=0;digest=sha256()
    try:
        with opener(original,"rb") as source,dest.open("wb") as target:
            while True:
                block=source.read(min(65536,limit-size+1))
                if not block:break
                size+=len(block)
                if size>limit:raise BoundedFailure("DECOMPRESSED_BYTES_EXCEED_LIMIT")
                digest.update(block);target.write(block)
    except Exception:
        dest.unlink(missing_ok=True)
        raise
    return {"decoded_format":kind,"uncompressed_sha256":digest.hexdigest(),
            "uncompressed_bytes":size}


def scan_dimacs(path:Path):
    """One-pass streaming DIMACS grammar check; handles clauses across lines.

    Comments start at beginning of physical line. At most one header.
    Each clause must close at 0 and variable within declared range.
    A strict budget enforces no memory-bomb or wide-clause explosion.
    """
    header=False;declared_vars=declared_rows=0
    rows=literals=0;max_width=0;current=0;header_count=0
    actually_used_var=0
    try:
        with path.open("r",encoding="ascii",errors="strict") as fp:
            for physical_line,line in enumerate(fp,1):
                striped=line.strip()
                if not striped or striped.startswith("c"):continue
                if striped.startswith("p"):
                    parts=striped.split()
                    if header or parts[:2]!=["p","cnf"] or len(parts)!=4 or current:
                        raise BoundedFailure("INVALID_OR_REPEATED_HEADER")
                    try:declared_vars=int(parts[2]);declared_rows=int(parts[3])
                    except ValueError as exc:raise BoundedFailure("INVALID_HEADER_NUMBERS") from exc
                    if declared_vars<1 or declared_vars>MAX_VARS_PARSE or declared_rows<0 or declared_rows>MAX_CLAUSES_PARSE:
                        raise BoundedFailure("DIMACS_HEADER_EXCEEDS_PARSER_BUDGET")
                    header=True;header_count+=1
                    continue
                if not header:raise BoundedFailure("DATA_BEFORE_DIMACS_HEADER")
                for tok in striped.split():
                    if not re.fullmatch(r"[+-]?[0-9]+",tok):
                        raise BoundedFailure("NON_INTEGER_DIMACS_TOKEN")
                    lit=int(tok)
                    if lit==0:
                        rows+=1;max_width=max(max_width,current);current=0
                        if rows>declared_rows:
                            raise BoundedFailure("CLAUSES_EXCEED_DECLARED")
                        continue
                    if abs(lit)>declared_vars:
                        raise BoundedFailure("LITERAL_VARIABLE_OUT_OF_RANGE")
                    actually_used_var=max(actually_used_var,abs(lit))
                    current+=1;literals+=1
                    if current>MAX_CLAUSE_WIDTH_PARSE or literals>MAX_LITERALS_PARSE:
                        raise BoundedFailure("DIMACS_LITERAL_BUDGET")
    except UnicodeError as exc:raise BoundedFailure("INVALID_ASCII_ENCODING") from exc
    if not header:raise BoundedFailure("MISSING_DIMACS_HEADER")
    if current:raise BoundedFailure("UNTERMINATED_CLAUSE")
    if rows!=declared_rows:raise BoundedFailure("DIMACS_CLAUSE_COUNT_MISMATCH")
    return {"n_variables":declared_vars,"n_clauses":rows,"n_literal_occurrences":literals,
            "max_clause_width":max_width,"max_observed_variable":actually_used_var,
            "suitable_for_bounded_solver":(
                declared_vars<=MAX_VARS_SOLVE and rows<=MAX_CLAUSES_SOLVE
                and literals<=MAX_LITERALS_SOLVE)}


def pilot(prereg, output):
    import subprocess
    expected_hash=subprocess.run(["git","hash-object",str(prereg)],
        check=True,capture_output=True,text=True).stdout.strip()
    if expected_hash!=GIT_BLOB_SHA:
        raise BoundedFailure("PRE_REGISTERED_CANDIDATES_FILE_BLOB_SHA_CHANGED")
    data=json.loads(prereg.read_text())
    cases=data.get("candidates",[])
    if len(cases)!=12 or {x["result"] for x in cases}!={"sat","unsat","unknown"}:
        raise BoundedFailure("EXPECTED_FROZEN_12_STRATA_MISSING")
    folder=output/"downloads";folder.mkdir(parents=True,exist_ok=True)
    records=[]
    for i,c in enumerate(cases):
        row={"index":i,"GBD_database_ID_NOT_SHA256":c["hash"],"family":c["family"],
             "author":c["author"],"upstream_label_UNVERIFIED":c["result"],
             "registered_source_uri":c["official_uri"],"status":"NOT_ATTEMPTED"}
        try:
            original,digest=retrieve(c,folder)
            row.update(digest)
            decoded=folder/(c["hash"]+".cnf")
            row.update(unpack_bounded(original,decoded))
            row.update(scan_dimacs(decoded))
            row["status"]="SOURCE_FETCHED_DIMACS_VALID"
            if not row["suitable_for_bounded_solver"]:
                row["solver_status"]="SKIPPED_SOLVER_SIZE_CAP"
            else:
                # Readable original and compressed bytes retained for
                # separate reversible recheck. Solver executable is a child.
                row["solver_status"]="READY_FOR_STRICT_BASELINE"
        except BoundedFailure as exc:
            row["status"]=exc.reason
        except Exception as exc:
            row["status"]="SOURCE_OR_PARSER_EXCEPTION"
            row["error_type"]=type(exc).__name__
        records.append(row)
        print("CASE",i,c["family"],row["status"],row.get("original_transfer_bytes",0),flush=True)
    manifest={
      "schema":"JANUS-TIME-SAT-004B-EXTERNAL-ORIGIN-DIMACS-ACQUISITION-V1",
      "original_corpus":"SAT Competition 2026 12 previously committed public candidate identities",
      "original_registered_git_blob_sha":GIT_BLOB_SHA,
      "GBD_id_not_sha256":True,"max_transfer_bytes_each":MAX_TRANSFER_BYTES,
      "max_decoded_bytes_each":MAX_DECOMPRESSED_BYTES,
      "status":"PUBLIC_SCREENING_INPUTS_ONLY_NO_HIDDEN_HOLDOUT",
      "registered_candidates":12,
      "retrieved":sum(r["status"]=="SOURCE_FETCHED_DIMACS_VALID" for r in records),
      "solver_feasible":sum(r.get("solver_status")=="READY_FOR_STRICT_BASELINE" for r in records),
      "results":records,"C023_production":"UNCHANGED"
    }
    output.mkdir(parents=True,exist_ok=True)
    (output/"acquisition.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print("SUMMARY",json.dumps({k:manifest[k] for k in ("retrieved","solver_feasible","registered_candidates")}),flush=True)
    return manifest


if __name__=="__main__":
    args=argparse.ArgumentParser()
    args.add_argument("--preregister",type=Path,default=Path(PRE_REG))
    args.add_argument("--out",type=Path,required=True)
    a=args.parse_args()
    try:pilot(a.preregister,a.out)
    except BoundedFailure as exc:
        print(json.dumps({"fatal":exc.reason}))
        sys.exit(2)
