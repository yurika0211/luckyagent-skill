#!/usr/bin/env bash
# Resolve a stable aoci binary path and print basic identity.
# Portable: no hard-coded usernames or machine paths.
set -euo pipefail

candidates=""
add_cand() {
  c="$1"
  case " $candidates " in
    *" $c "*) ;;
    *) candidates="$candidates $c" ;;
  esac
}

if command -v aoci >/dev/null 2>&1; then
  add_cand "$(command -v aoci)"
fi
if [ -n "${HOME:-}" ] && [ -x "${HOME}/.local/bin/aoci" ]; then
  add_cand "${HOME}/.local/bin/aoci"
fi
# common source-checkout locations relative to cwd / parent trees
for rel in ./build/aoci ../aoci-code/build/aoci ../../aoci-code/build/aoci; do
  if [ -x "$rel" ]; then
    # resolve without requiring GNU realpath
    dir=$(CDPATH= cd -- "$(dirname "$rel")" && pwd -P)
    add_cand "$dir/$(basename "$rel")"
  fi
done

candidates=$(printf '%s' "$candidates" | sed 's/^ *//')
if [ -z "$candidates" ]; then
  echo "aoci not found. Install a release binary or build from https://github.com/aoci-spec/aoci-code" >&2
  exit 1
fi

bin=$(printf '%s\n' $candidates | awk 'NF{print; exit}')
printf 'AOCI_BIN=%s\n' "$bin"
"$bin" --version
if [ "${1:-}" = "--json-capabilities" ]; then
  repo="${2:-.}"
  "$bin" --repo "$repo" --json capabilities
fi
