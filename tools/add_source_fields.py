#!/usr/bin/env python3
"""Inject the root fields altgen does not emit into a merged AltStore source.

AltStore's source format (and TrollStore, which reads the same format)
requires a root `identifier` and `sourceURL`. altgen merge only writes
name/subtitle/description/icon_url/website/tint_color, so a source built by
altgen alone has neither — TrollStore rejects it as an invalid connection
("连接无效") when the source is added.

Run after `altgen merge`, before `tools/make_proxy.py`, so the proxy mirror
rewrites sourceURL to the gh-proxy URL automatically (make_proxy.py rewrites
every raw.githubusercontent.com URL it finds, and leaves `identifier` alone).

Stdlib only, so the bare system `python3` runs it. Idempotent: re-running
just sets the same two keys again.

Usage:
  python3 tools/add_source_fields.py added-apps.json
  python3 tools/add_source_fields.py added-apps.json --identifier com.example.source --source-url https://example.com/added-apps.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

DEFAULT_IDENTIFIER = "com.haly0ung.altgallery-added"
DEFAULT_SOURCE_URL = (
    "https://raw.githubusercontent.com/haly0ung/AltGallery-Added/"
    "master/added-apps.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Add identifier and sourceURL to a merged source JSON."
    )
    parser.add_argument("input", type=Path, help="source JSON to patch in place")
    parser.add_argument(
        "--identifier",
        default=DEFAULT_IDENTIFIER,
        help=f"source identifier (default: {DEFAULT_IDENTIFIER})",
    )
    parser.add_argument(
        "--source-url",
        default=DEFAULT_SOURCE_URL,
        help=f"source URL (default: {DEFAULT_SOURCE_URL})",
    )
    args = parser.parse_args()

    try:
        source = json.loads(args.input.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"Error: cannot read {args.input}: {exc}")
        return 1
    except json.JSONDecodeError as exc:
        print(f"Error: {args.input} is not valid JSON: {exc}")
        return 1

    source["identifier"] = args.identifier
    source["sourceURL"] = args.source_url
    args.input.write_text(
        json.dumps(source, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Set identifier={args.identifier} sourceURL={args.source_url} in {args.input}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
