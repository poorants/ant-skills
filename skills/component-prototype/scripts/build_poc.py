#!/usr/bin/env python3
"""Assemble a single-file POC review page from the shipped shell + a round's data JS.

The shell (assets/poc-shell.html) holds all the interactive plumbing — voting checkboxes,
tabs (round candidates / carried-forward finalists), sample toggle, localStorage persistence,
and clipboard JSON export. Each round you only author a small JS file that defines
`window.POC_SPEC` (theme tokens + candidate render functions); this script inlines it into the
shell at the `/*__POC_DATA__*/` sentinel and writes a standalone HTML you can open directly.

Usage:
    python build_poc.py --data poc-data.js --out poc-round-2.html
    python build_poc.py --data poc-data.js --out out.html --shell /custom/shell.html --open

See ../references/data-contract.md for the POC_SPEC shape and a worked example.
"""
import argparse
import os
import sys
import webbrowser

SENTINEL = "/*__POC_DATA__*/"


def main() -> int:
    ap = argparse.ArgumentParser(description="Build a single-file component-POC review page.")
    ap.add_argument("--data", required=True, help="Path to the round's data JS (defines window.POC_SPEC).")
    ap.add_argument("--out", required=True, help="Path to write the assembled HTML.")
    ap.add_argument("--shell", default=None, help="Override shell path (defaults to the shipped assets/poc-shell.html).")
    ap.add_argument("--open", action="store_true", help="Open the result in the default browser.")
    args = ap.parse_args()

    shell_path = args.shell or os.path.join(os.path.dirname(__file__), "..", "assets", "poc-shell.html")
    shell_path = os.path.abspath(shell_path)
    if not os.path.exists(shell_path):
        print(f"shell not found: {shell_path}", file=sys.stderr)
        return 1
    if not os.path.exists(args.data):
        print(f"data not found: {args.data}", file=sys.stderr)
        return 1

    with open(shell_path, encoding="utf-8") as f:
        shell = f.read()
    with open(args.data, encoding="utf-8") as f:
        data = f.read()

    if SENTINEL not in shell:
        print(f"sentinel {SENTINEL!r} missing from shell — wrong template?", file=sys.stderr)
        return 1

    # Plain string replacement: data is JS, shell slot is inside a <script>, so no escaping needed.
    # Guard only against an accidental </script> in the data that would close the tag early.
    if "</script" in data.lower():
        print("data JS contains '</script' which would break injection — encode it (e.g. '<\\/script').", file=sys.stderr)
        return 1

    html = shell.replace(SENTINEL, data)
    out = os.path.abspath(args.out)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"wrote {out}  ({len(html):,} bytes)")

    if args.open:
        webbrowser.open("file://" + out.replace(os.sep, "/"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
