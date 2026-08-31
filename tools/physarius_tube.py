#!/usr/bin/env python3
"""JANUS Physarius Tube: range-based siphon for very large remote ZIP archives.

Design goals:
- stdlib only;
- inspect ZIP/ZIP64 central directory without downloading the full archive;
- blind-by-default member index (hash IDs instead of names);
- selectively extract one member by hashed ID using HTTP Range requests;
- fail closed when the server ignores Range or archive structure is unsupported.

This is a data-access utility. It does not interpret scientific content.
"""
from __future__ import annotations

import argparse
import binascii
import hashlib
import json
import re
import struct
import sys
import urllib.parse
import urllib.request
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

EOCD_SIG = b"PK\x05\x06"
ZIP64_LOC_SIG = b"PK\x06\x07"
ZIP64_EOCD_SIG = b"PK\x06\x06"
CD_SIG = b"PK\x01\x02"
LOCAL_SIG = b"PK\x03\x04"
ZIP64_EXTRA_ID = 0x0001
MAX_U16 = 0xFFFF
MAX_U32 = 0xFFFFFFFF
DEFAULT_TAIL = 256 * 1024
DEFAULT_RANGE_CHUNK = 8 * 1024 * 1024


def _json_dump(obj, path: Optional[str]) -> None:
    text = json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if path:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


class RangeError(RuntimeError):
    pass


class ByteSource:
    url: str

    def size(self) -> int:
        raise NotImplementedError

    def read_range(self, start: int, end: int) -> bytes:
        raise NotImplementedError


class FileRangeSource(ByteSource):
    def __init__(self, path: str):
        self.path = Path(path)
        self.url = self.path.resolve().as_uri()
        self._size = self.path.stat().st_size

    def size(self) -> int:
        return self._size

    def read_range(self, start: int, end: int) -> bytes:
        if start < 0 or end < start or end >= self._size:
            raise RangeError(f"invalid local range {start}-{end} for {self._size}")
        with self.path.open("rb") as f:
            f.seek(start)
            data = f.read(end - start + 1)
        if len(data) != end - start + 1:
            raise RangeError("short local read")
        return data


class HttpRangeSource(ByteSource):
    def __init__(self, url: str, timeout: int = 60, user_agent: str = "JANUS-Physarius-Tube/1.0"):
        self.url = url
        self.timeout = timeout
        self.user_agent = user_agent
        self._size: Optional[int] = None
        self.last_headers = {}

    def _request(self, start: int, end: int):
        req = urllib.request.Request(
            self.url,
            headers={
                "Range": f"bytes={start}-{end}",
                "User-Agent": self.user_agent,
                "Accept-Encoding": "identity",
            },
            method="GET",
        )
        return urllib.request.urlopen(req, timeout=self.timeout)

    def size(self) -> int:
        if self._size is not None:
            return self._size
        try:
            with self._request(0, 0) as r:
                self.last_headers = dict(r.headers.items())
                status = getattr(r, "status", None) or r.getcode()
                cr = r.headers.get("Content-Range")
                if status == 206 and cr:
                    m = re.match(r"bytes\s+\d+-\d+/(\d+)$", cr.strip(), re.I)
                    if not m:
                        raise RangeError(f"unparseable Content-Range: {cr!r}")
                    self._size = int(m.group(1))
                    r.read(1)
                    return self._size
                if status == 200:
                    length = r.headers.get("Content-Length")
                    raise RangeError(
                        "server ignored HTTP Range (returned 200); refusing full-body transfer"
                        + (f"; Content-Length={length}" if length else "")
                    )
                raise RangeError(f"unexpected HTTP status {status} during range probe")
        except Exception as e:
            if isinstance(e, RangeError):
                raise
            raise RangeError(f"range probe failed: {e}") from e

    def read_range(self, start: int, end: int) -> bytes:
        total = self.size()
        if start < 0 or end < start or end >= total:
            raise RangeError(f"invalid HTTP range {start}-{end} for {total}")
        try:
            with self._request(start, end) as r:
                status = getattr(r, "status", None) or r.getcode()
                if status != 206:
                    raise RangeError(f"server ignored/failed range {start}-{end}: HTTP {status}")
                cr = r.headers.get("Content-Range", "")
                if not cr.lower().startswith(f"bytes {start}-{end}/".lower()):
                    raise RangeError(f"range mismatch: requested {start}-{end}, got {cr!r}")
                data = r.read(end - start + 1)
                if len(data) != end - start + 1:
                    raise RangeError(f"short HTTP range read: {len(data)} != {end-start+1}")
                return data
        except Exception as e:
            if isinstance(e, RangeError):
                raise
            raise RangeError(f"range read failed {start}-{end}: {e}") from e


def make_source(url: str, timeout: int = 60) -> ByteSource:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme in ("", "file"):
        path = urllib.request.url2pathname(parsed.path) if parsed.scheme == "file" else url
        return FileRangeSource(path)
    if parsed.scheme in ("http", "https"):
        return HttpRangeSource(url, timeout=timeout)
    raise ValueError(f"unsupported URL scheme: {parsed.scheme}")


def zenodo_file_url(record_id: str, filename: str) -> str:
    return f"https://zenodo.org/records/{record_id}/files/{urllib.parse.quote(filename)}?download=1"


@dataclass
class ZipEntry:
    ordinal: int
    name: str
    raw_name: bytes
    flags: int
    method: int
    crc32: int
    compressed_size: int
    uncompressed_size: int
    local_header_offset: int
    disk_start: int

    @property
    def member_id(self) -> str:
        return hashlib.sha256(self.raw_name).hexdigest()

    @property
    def extension(self) -> str:
        if self.name.endswith("/"):
            return ""
        return Path(self.name).suffix.lower()

    def to_dict(self, reveal_names: bool = False) -> dict:
        d = {
            "ordinal": self.ordinal,
            "member_id": self.member_id,
            "extension": self.extension,
            "is_directory": self.name.endswith("/"),
            "flags": self.flags,
            "compression_method": self.method,
            "crc32_hex": f"{self.crc32:08x}",
            "compressed_size": self.compressed_size,
            "uncompressed_size": self.uncompressed_size,
            "local_header_offset": self.local_header_offset,
            "disk_start": self.disk_start,
        }
        if reveal_names:
            d["name"] = self.name
        return d


@dataclass
class ZipIndex:
    archive_size: int
    central_directory_offset: int
    central_directory_size: int
    total_entries: int
    zip64: bool
    entries: list[ZipEntry]


def _parse_zip64_extra(extra: bytes, need_uncomp: bool, need_comp: bool, need_offset: bool, need_disk: bool):
    pos = 0
    payload = None
    while pos + 4 <= len(extra):
        header_id, size = struct.unpack_from("<HH", extra, pos)
        pos += 4
        body = extra[pos:pos + size]
        pos += size
        if header_id == ZIP64_EXTRA_ID:
            payload = body
            break
    if payload is None:
        raise RangeError("ZIP64 sentinel present but ZIP64 extra field missing")
    p = 0
    out = {}

    def take_q(key):
        nonlocal p
        if p + 8 > len(payload):
            raise RangeError("truncated ZIP64 extra field")
        out[key] = struct.unpack_from("<Q", payload, p)[0]
        p += 8

    def take_l(key):
        nonlocal p
        if p + 4 > len(payload):
            raise RangeError("truncated ZIP64 disk field")
        out[key] = struct.unpack_from("<L", payload, p)[0]
        p += 4

    if need_uncomp:
        take_q("uncomp")
    if need_comp:
        take_q("comp")
    if need_offset:
        take_q("offset")
    if need_disk:
        take_l("disk")
    return out


def read_zip_index(source: ByteSource, tail_bytes: int = DEFAULT_TAIL) -> ZipIndex:
    total = source.size()
    tail_len = min(total, max(tail_bytes, 65557))
    tail_start = total - tail_len
    tail = source.read_range(tail_start, total - 1)
    eocd_rel = tail.rfind(EOCD_SIG)
    if eocd_rel < 0:
        raise RangeError("EOCD not found in archive tail; increase --tail-bytes or archive may not be ZIP")
    eocd_abs = tail_start + eocd_rel
    if eocd_rel + 22 > len(tail):
        raise RangeError("truncated EOCD")
    sig, disk_no, cd_disk, entries_disk, entries_total, cd_size32, cd_off32, comment_len = struct.unpack_from(
        "<4s4H2LH", tail, eocd_rel
    )
    if sig != EOCD_SIG:
        raise RangeError("bad EOCD signature")
    if disk_no != 0 or cd_disk != 0:
        raise RangeError("multi-disk ZIP is not supported")

    use_zip64 = entries_total == MAX_U16 or cd_size32 == MAX_U32 or cd_off32 == MAX_U32
    entries = int(entries_total)
    cd_size = int(cd_size32)
    cd_offset = int(cd_off32)

    if use_zip64:
        loc_abs = eocd_abs - 20
        if loc_abs < 0:
            raise RangeError("ZIP64 locator position invalid")
        loc = source.read_range(loc_abs, eocd_abs - 1)
        if len(loc) != 20:
            raise RangeError("truncated ZIP64 locator")
        sig2, disk64, eocd64_off, total_disks = struct.unpack("<4sLQL", loc)
        if sig2 != ZIP64_LOC_SIG:
            loc_rel = tail.rfind(ZIP64_LOC_SIG, 0, eocd_rel)
            if loc_rel < 0 or loc_rel + 20 > len(tail):
                raise RangeError("ZIP64 locator not found")
            sig2, disk64, eocd64_off, total_disks = struct.unpack_from("<4sLQL", tail, loc_rel)
        if total_disks != 1 or disk64 != 0:
            raise RangeError("multi-disk ZIP64 is not supported")
        fixed = source.read_range(eocd64_off, eocd64_off + 55)
        vals = struct.unpack("<4sQ2H2L4Q", fixed)
        if vals[0] != ZIP64_EOCD_SIG:
            raise RangeError("bad ZIP64 EOCD signature")
        _, rec_size, ver_made, ver_need, disk_no64, cd_disk64, entries_disk64, entries_total64, cd_size64, cd_off64 = vals
        if disk_no64 != 0 or cd_disk64 != 0:
            raise RangeError("multi-disk ZIP64 is not supported")
        entries = int(entries_total64)
        cd_size = int(cd_size64)
        cd_offset = int(cd_off64)

    if cd_size <= 0 or cd_offset < 0 or cd_offset + cd_size > total:
        raise RangeError(f"central directory bounds invalid: offset={cd_offset} size={cd_size} total={total}")
    cd = source.read_range(cd_offset, cd_offset + cd_size - 1)
    result: list[ZipEntry] = []
    pos = 0
    ordinal = 0
    while pos < len(cd):
        if pos + 46 > len(cd):
            raise RangeError(f"truncated central-directory header at {pos}")
        fields = struct.unpack_from("<4s6H3L5H2L", cd, pos)
        if fields[0] != CD_SIG:
            raise RangeError(f"unexpected central-directory signature at {pos}: {fields[0]!r}")
        (
            _, ver_made, ver_need, flags, method, mtime, mdate, crc32,
            comp32, uncomp32, name_len, extra_len, member_comment_len, disk_start16,
            int_attr, ext_attr, local_off32,
        ) = fields
        start = pos + 46
        name_b = cd[start:start + name_len]
        extra = cd[start + name_len:start + name_len + extra_len]
        if len(name_b) != name_len or len(extra) != extra_len:
            raise RangeError("truncated filename/extra in central directory")
        encoding = "utf-8" if (flags & (1 << 11)) else "cp437"
        name = name_b.decode(encoding, errors="replace")
        comp = int(comp32)
        uncomp = int(uncomp32)
        local_off = int(local_off32)
        disk_start = int(disk_start16)
        need_uncomp = uncomp32 == MAX_U32
        need_comp = comp32 == MAX_U32
        need_offset = local_off32 == MAX_U32
        need_disk = disk_start16 == MAX_U16
        if need_uncomp or need_comp or need_offset or need_disk:
            z = _parse_zip64_extra(extra, need_uncomp, need_comp, need_offset, need_disk)
            uncomp = int(z.get("uncomp", uncomp))
            comp = int(z.get("comp", comp))
            local_off = int(z.get("offset", local_off))
            disk_start = int(z.get("disk", disk_start))
        result.append(ZipEntry(ordinal, name, name_b, flags, method, crc32, comp, uncomp, local_off, disk_start))
        ordinal += 1
        pos = start + name_len + extra_len + member_comment_len

    if entries != len(result):
        raise RangeError(f"entry-count mismatch: EOCD={entries}, parsed={len(result)}")
    return ZipIndex(total, cd_offset, cd_size, entries, use_zip64, result)


def probe(source: ByteSource) -> dict:
    size = source.size()
    tail = source.read_range(max(0, size - 64), size - 1)
    return {
        "status": "RANGE_OK",
        "source": source.url,
        "archive_size": size,
        "tail_probe_sha256": hashlib.sha256(tail).hexdigest(),
        "tail_probe_bytes": len(tail),
        "http_headers": getattr(source, "last_headers", {}),
    }


def index_receipt(source: ByteSource, reveal_names: bool, tail_bytes: int) -> dict:
    idx = read_zip_index(source, tail_bytes=tail_bytes)
    entries = [e.to_dict(reveal_names=reveal_names) for e in idx.entries]
    return {
        "status": "INDEX_OK",
        "blind_by_default": not reveal_names,
        "source": source.url,
        "archive_size": idx.archive_size,
        "zip64": idx.zip64,
        "central_directory_offset": idx.central_directory_offset,
        "central_directory_size": idx.central_directory_size,
        "total_entries": idx.total_entries,
        "entries": entries,
        "index_sha256": hashlib.sha256(
            json.dumps(entries, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    }


def _local_data_offset(source: ByteSource, entry: ZipEntry) -> int:
    fixed = source.read_range(entry.local_header_offset, entry.local_header_offset + 29)
    vals = struct.unpack("<4s5H3L2H", fixed)
    if vals[0] != LOCAL_SIG:
        raise RangeError(f"bad local header for member {entry.member_id}")
    _, ver_need, flags, method, mtime, mdate, crc, comp32, uncomp32, name_len, extra_len = vals
    if method != entry.method:
        raise RangeError("local/central compression-method mismatch")
    return entry.local_header_offset + 30 + name_len + extra_len


def _find_entry(idx: ZipIndex, member_id: Optional[str], name: Optional[str]) -> ZipEntry:
    if bool(member_id) == bool(name):
        raise ValueError("provide exactly one of --member-id or --name")
    if member_id:
        hits = [e for e in idx.entries if e.member_id == member_id.lower()]
    else:
        hits = [e for e in idx.entries if e.name == name]
    if len(hits) != 1:
        raise RangeError(f"member selector resolved to {len(hits)} entries")
    return hits[0]


def extract_entry(source: ByteSource, entry: ZipEntry, output: str, chunk_size: int, max_output_bytes: int) -> dict:
    if entry.name.endswith("/"):
        raise RangeError("cannot extract directory entry")
    if entry.uncompressed_size > max_output_bytes:
        raise RangeError(
            f"member exceeds max output guard: {entry.uncompressed_size} > {max_output_bytes}; "
            "raise --max-output-bytes explicitly if intended"
        )
    if entry.flags & 0x1:
        raise RangeError("encrypted ZIP member is not supported")
    if entry.method not in (0, 8):
        raise RangeError(f"compression method {entry.method} unsupported (only stored=0, deflate=8)")
    data_offset = _local_data_offset(source, entry)
    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sha = hashlib.sha256()
    crc = 0
    written = 0
    decomp = zlib.decompressobj(-zlib.MAX_WBITS) if entry.method == 8 else None
    remaining = entry.compressed_size
    cursor = data_offset
    with out_path.open("wb") as f:
        while remaining:
            n = min(chunk_size, remaining)
            block = source.read_range(cursor, cursor + n - 1)
            cursor += n
            remaining -= n
            plain = decomp.decompress(block) if decomp else block
            if plain:
                f.write(plain)
                sha.update(plain)
                crc = binascii.crc32(plain, crc)
                written += len(plain)
                if written > max_output_bytes:
                    raise RangeError("output guard exceeded during decompression")
        if decomp:
            plain = decomp.flush()
            if plain:
                f.write(plain)
                sha.update(plain)
                crc = binascii.crc32(plain, crc)
                written += len(plain)
    crc &= 0xFFFFFFFF
    if written != entry.uncompressed_size:
        raise RangeError(f"uncompressed size mismatch: {written} != {entry.uncompressed_size}")
    if crc != entry.crc32:
        raise RangeError(f"CRC32 mismatch: {crc:08x} != {entry.crc32:08x}")
    return {
        "status": "PULL_OK",
        "source": source.url,
        "member_id": entry.member_id,
        "extension": entry.extension,
        "compressed_size": entry.compressed_size,
        "uncompressed_size": entry.uncompressed_size,
        "crc32_verified": f"{crc:08x}",
        "sha256": sha.hexdigest(),
        "output": str(out_path),
    }


def build_url(args) -> str:
    if args.url:
        return args.url
    if args.record_id and args.filename:
        return zenodo_file_url(args.record_id, args.filename)
    raise SystemExit("provide --url or both --record-id and --filename")


def main(argv: Optional[Iterable[str]] = None) -> int:
    p = argparse.ArgumentParser(description="JANUS Physarius Tube: remote ZIP/ZIP64 range siphon")
    p.add_argument("--url", help="Direct http(s), file://, or local archive path")
    p.add_argument("--record-id", help="Zenodo record ID")
    p.add_argument("--filename", help="Zenodo filename")
    p.add_argument("--timeout", type=int, default=60)
    p.add_argument("--tail-bytes", type=int, default=DEFAULT_TAIL)
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("probe", help="Verify random-access range capability")
    sp.add_argument("--json-out")

    si = sub.add_parser("index", help="Read ZIP central directory without full download")
    si.add_argument("--reveal-names", action="store_true", help="UNBLIND: include plaintext member names")
    si.add_argument("--json-out")

    sl = sub.add_parser("list", help="Alias of index; blind unless --reveal-names")
    sl.add_argument("--reveal-names", action="store_true")
    sl.add_argument("--json-out")

    sx = sub.add_parser("pull", help="Range-extract exactly one archive member")
    sx.add_argument("--member-id", help="Blind SHA256 ID emitted by index")
    sx.add_argument("--name", help="UNBLIND plaintext member name")
    sx.add_argument("--output", required=True)
    sx.add_argument("--chunk-bytes", type=int, default=DEFAULT_RANGE_CHUNK)
    sx.add_argument("--max-output-bytes", type=int, default=512 * 1024 * 1024)
    sx.add_argument("--allow-content", action="store_true", help="Required acknowledgement before extracting member content")
    sx.add_argument("--receipt-out")

    args = p.parse_args(list(argv) if argv is not None else None)
    url = build_url(args)
    source = make_source(url, timeout=args.timeout)
    if args.cmd == "probe":
        _json_dump(probe(source), args.json_out)
        return 0
    if args.cmd in ("index", "list"):
        _json_dump(index_receipt(source, args.reveal_names, args.tail_bytes), args.json_out)
        return 0
    if args.cmd == "pull":
        if not args.allow_content:
            raise SystemExit("pull is content-unblinding; pass --allow-content explicitly")
        idx = read_zip_index(source, tail_bytes=args.tail_bytes)
        entry = _find_entry(idx, args.member_id, args.name)
        receipt = extract_entry(source, entry, args.output, args.chunk_bytes, args.max_output_bytes)
        _json_dump(receipt, args.receipt_out)
        return 0
    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RangeError as e:
        sys.stderr.write(f"PHYSARIUS_BLOCKED: {e}\n")
        raise SystemExit(3)
