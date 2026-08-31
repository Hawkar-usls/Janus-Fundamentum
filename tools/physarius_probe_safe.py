#!/usr/bin/env python3
"""Safe probe wrapper for JANUS Physarius Tube.

Only a small whitelist of transport headers is retained in receipts. Cookies,
authentication material, rate-limit metadata and unrelated response headers are
never written to the artifact.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from physarius_tube import make_source, probe, zenodo_file_url

SAFE_HEADERS = {
    "accept-ranges",
    "content-range",
    "content-length",
    "content-type",
    "content-disposition",
    "etag",
    "last-modified",
    "x-source",
}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--url")
    p.add_argument("--record-id")
    p.add_argument("--filename")
    p.add_argument("--timeout", type=int, default=60)
    p.add_argument("--json-out", required=True)
    args = p.parse_args()

    if args.url:
        url = args.url
    elif args.record_id and args.filename:
        url = zenodo_file_url(args.record_id, args.filename)
    else:
        raise SystemExit("provide --url or both --record-id and --filename")

    receipt = probe(make_source(url, timeout=args.timeout))
    headers = receipt.get("http_headers") or {}
    receipt["http_headers"] = {
        str(k).lower(): v
        for k, v in headers.items()
        if str(k).lower() in SAFE_HEADERS
    }
    receipt["header_policy"] = "SAFE_WHITELIST_ONLY"

    out = Path(args.json_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
