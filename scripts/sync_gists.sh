#!/usr/bin/env bash
# Re-sync the public install gists FROM the local bootstrap scripts (single source of truth).
#
# The README one-liner serves bootstrap/init-claude-project.{sh,ps1} from the repo; these two
# gists mirror them for anyone who installs via the gist URLs. Whenever the bootstrap scripts
# change, run this to keep the gists identical.
#
# Requires: gh (authenticated as the gist owner), python3.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

SH_GIST=290c69ac4b005606b7462b9e024241a0    # file: init-claude-project.sh
PS1_GIST=d0a171631512f02534248b8c5c4a542c   # file: init-claude-project.ps1

patch_gist() {  # <gist-id> <filename-in-gist> <local-path>
  local id="$1" fname="$2" path="$3"
  python3 -c "import json,sys; print(json.dumps({'files': {sys.argv[1]: {'content': open(sys.argv[2], encoding='utf-8').read()}}}))" \
    "$fname" "$path" \
    | gh api -X PATCH "/gists/$id" --input - -q '.html_url'
}

echo "[...] $SH_GIST  <- bootstrap/init-claude-project.sh"
patch_gist "$SH_GIST" "init-claude-project.sh" "$ROOT/bootstrap/init-claude-project.sh"

echo "[...] $PS1_GIST <- bootstrap/init-claude-project.ps1"
patch_gist "$PS1_GIST" "init-claude-project.ps1" "$ROOT/bootstrap/init-claude-project.ps1"

echo "[OK] gists synced from local bootstrap scripts"
