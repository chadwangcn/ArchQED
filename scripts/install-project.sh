#!/usr/bin/env bash
set -euo pipefail
SOURCE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${1:-$PWD}"
STAGE="${2:-discovery}"
case "$STAGE" in discovery|stabilizing|delivery) ;; *) echo "invalid stage" >&2; exit 2;; esac
mkdir -p "$TARGET"
TARGET="$(cd "$TARGET" && pwd)"
python -m pip install --no-deps "$SOURCE"
mkdir -p "$TARGET/.agents/skills" "$TARGET/.codex/agents" "$TARGET/scripts"
for skill in archqed-compile archqed-implement archqed-verify; do
  rm -rf "$TARGET/.agents/skills/$skill"
  cp -R "$SOURCE/.agents/skills/$skill" "$TARGET/.agents/skills/$skill"
done
cp "$SOURCE/.codex/agents/archqed-"*.toml "$TARGET/.codex/agents/"
if [[ ! -f "$TARGET/.codex/config.toml" ]]; then cp "$SOURCE/.codex/config.toml" "$TARGET/.codex/config.toml"; else echo "Existing .codex/config.toml preserved." >&2; fi
for script in codex-sync.sh codex-next.sh codex-verify.sh; do cp "$SOURCE/scripts/$script" "$TARGET/scripts/$script"; chmod +x "$TARGET/scripts/$script"; done
START='# >>> ArchQED managed instructions >>>'; END='# <<< ArchQED managed instructions <<<'
AGENTS="$TARGET/AGENTS.md"; TMP="$(mktemp)"
if [[ -f "$AGENTS" ]]; then awk -v start="$START" -v end="$END" '$0==start{skip=1;next}$0==end{skip=0;next}!skip{print}' "$AGENTS" > "$TMP"; fi
{ cat "$TMP" 2>/dev/null || true; printf '\n%s\n' "$START"; cat "$SOURCE/AGENTS.md"; printf '%s\n' "$END"; } > "$AGENTS"
rm -f "$TMP"
if [[ ! -f "$TARGET/.archqed/config.json" ]]; then archqed --root "$TARGET" init --name "$(basename "$TARGET")" --stage "$STAGE"; fi
echo "ArchQED installed in $TARGET"
echo "Next: edit docs, run archqed sync, then scripts/codex-sync.sh"
