#!/bin/sh

set -eu

mode=install
target_dir=''
while [ "$#" -gt 0 ]; do
  case "$1" in
    --check)
      mode=check
      shift
      ;;
    --target-dir)
      [ "$#" -ge 2 ] || { printf '%s\n' 'ERROR: --target-dir requires a path' >&2; exit 2; }
      [ -n "$2" ] || { printf '%s\n' 'ERROR: --target-dir requires a non-empty path' >&2; exit 2; }
      target_dir=$2
      shift 2
      ;;
    --help|-h)
      printf '%s\n' 'Usage: sh install.sh [--check] [--target-dir PATH]'
      exit 0
      ;;
    *)
      printf '%s\n' "ERROR: unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
payload_root=$script_dir/payload
source_agents=$payload_root/agents
source_skill=$payload_root/skills/route-subagents
source_routing=$payload_root/AGENTS.routing.md

if [ -n "$target_dir" ]; then
  codex_home=$target_dir
elif [ -n "${CODEX_HOME-}" ]; then
  codex_home=$CODEX_HOME
else
  : "${HOME:?HOME is unset and CODEX_HOME was not supplied}"
  codex_home=$HOME/.codex
fi

case "$codex_home" in
  /|//) printf '%s\n' "ERROR: refusing to use the filesystem root as CODEX_HOME" >&2; exit 1 ;;
esac

begin_marker='<!-- BEGIN CODEX-AGENT-CONFIG ROUTING -->'
end_marker='<!-- END CODEX-AGENT-CONFIG ROUTING -->'
timestamp=$(date -u '+%Y%m%dT%H%M%SZ')
backup_root=''
failures=0
changed=0

tmp_root=$(mktemp -d "${TMPDIR:-/tmp}/codex-agent-config.XXXXXX")
trap 'rm -rf "$tmp_root"' EXIT HUP INT TERM

fail() {
  printf '%s\n' "ERROR: $*" >&2
  exit 1
}

assert_regular_source() {
  [ -f "$1" ] && [ ! -L "$1" ] || fail "required source is missing or unsafe: $1"
}

assert_safe_destination() {
  if [ -L "$1" ]; then
    fail "refusing to replace a linked destination: $1"
  fi
  if [ -e "$1" ] && [ ! -f "$1" ]; then
    fail "expected a file but found another object: $1"
  fi
}

ensure_backup_root() {
  if [ -z "$backup_root" ]; then
    backup_root=$codex_home/backups/codex-agent-config/$timestamp
    mkdir -p "$backup_root" || fail "could not create backup directory: $backup_root"
  fi
}

backup_existing() {
  destination=$1
  relative=$2
  [ -f "$destination" ] || return 0
  ensure_backup_root
  backup_path=$backup_root/$relative
  mkdir -p "$(dirname -- "$backup_path")" || fail "could not create backup parent: $backup_path"
  cp "$destination" "$backup_path" || fail "could not back up: $destination"
}

copy_atomically() {
  source=$1
  destination=$2
  parent=$(dirname -- "$destination")
  mkdir -p "$parent" || fail "could not create destination parent: $parent"
  staged=$(mktemp "$parent/.codex-agent-config.XXXXXX") || fail "could not stage: $destination"
  if ! cp "$source" "$staged"; then
    rm -f "$staged"
    fail "could not copy: $source"
  fi
  if ! mv -f "$staged" "$destination"; then
    rm -f "$staged"
    fail "could not install: $destination"
  fi
}

install_file() {
  source=$1
  destination=$2
  relative=$3
  assert_regular_source "$source"
  assert_safe_destination "$destination"

  if [ -f "$destination" ] && cmp -s "$source" "$destination"; then
    printf '%s\n' "CURRENT  $relative"
    return 0
  fi

  if [ "$mode" = check ]; then
    printf '%s\n' "DIFF     $relative"
    failures=$((failures + 1))
    return 0
  fi

  backup_existing "$destination" "$relative"
  copy_atomically "$source" "$destination"
  cmp -s "$source" "$destination" || fail "post-install verification failed: $destination"
  printf '%s\n' "INSTALLED $relative"
  changed=$((changed + 1))
}

assert_regular_source "$source_routing"
find "$source_agents" -type f -name '*.toml' -print | sort > "$tmp_root/agents.list"
agent_count=$(wc -l < "$tmp_root/agents.list" | tr -d ' ')
[ "$agent_count" = 19 ] || fail "expected 19 custom-agent profiles, found $agent_count"

find "$source_skill" -type f -print | sort > "$tmp_root/skill.list"
skill_count=$(wc -l < "$tmp_root/skill.list" | tr -d ' ')
[ "$skill_count" -ge 3 ] || fail "route-subagents skill payload is incomplete"

while IFS= read -r source; do
  name=${source##*/}
  install_file "$source" "$codex_home/agents/$name" "agents/$name"
done < "$tmp_root/agents.list"

skill_prefix=$source_skill/
while IFS= read -r source; do
  relative_inside=${source#"$skill_prefix"}
  install_file "$source" "$codex_home/skills/route-subagents/$relative_inside" "skills/route-subagents/$relative_inside"
done < "$tmp_root/skill.list"

{
  printf '%s\n' "$begin_marker"
  sed 's/\r$//' "$source_routing"
  printf '%s\n' "$end_marker"
} > "$tmp_root/managed-block"

global_agents=$codex_home/AGENTS.md
assert_safe_destination "$global_agents"

if [ -f "$global_agents" ]; then
  begin_count=$(sed 's/\r$//' "$global_agents" | grep -F -x -c "$begin_marker" || true)
  end_count=$(sed 's/\r$//' "$global_agents" | grep -F -x -c "$end_marker" || true)
else
  begin_count=0
  end_count=0
fi

if [ "$begin_count" -gt 1 ] || [ "$end_count" -gt 1 ] || [ "$begin_count" -ne "$end_count" ]; then
  fail "invalid managed routing markers in $global_agents"
fi

if [ "$begin_count" -eq 1 ]; then
  awk -v begin="$begin_marker" -v end="$end_marker" '
    { line=$0; sub(/\r$/, "", line) }
    line == begin { inside=1 }
    inside { print }
    line == end { inside=0; found=1 }
    END { if (!found) exit 2 }
  ' "$global_agents" | sed 's/\r$//' > "$tmp_root/existing-block"
else
  : > "$tmp_root/existing-block"
fi

if cmp -s "$tmp_root/managed-block" "$tmp_root/existing-block"; then
  printf '%s\n' 'CURRENT  AGENTS.md managed routing block'
else
  if [ "$mode" = check ]; then
    printf '%s\n' 'DIFF     AGENTS.md managed routing block'
    failures=$((failures + 1))
  else
    backup_existing "$global_agents" 'AGENTS.md'
    if [ -f "$global_agents" ] && [ "$begin_count" -eq 1 ]; then
      awk -v begin="$begin_marker" -v end="$end_marker" '
        { line=$0; sub(/\r$/, "", line) }
        line == begin { skip=1; next }
        line == end { skip=0; next }
        !skip { print }
      ' "$global_agents" > "$tmp_root/preserved-agents"
    elif [ -f "$global_agents" ]; then
      sed 's/\r$//' "$global_agents" > "$tmp_root/existing-normalized"
      sed 's/\r$//' "$source_routing" > "$tmp_root/routing-normalized"
      if cmp -s "$tmp_root/existing-normalized" "$tmp_root/routing-normalized"; then
        : > "$tmp_root/preserved-agents"
      else
        cp "$tmp_root/existing-normalized" "$tmp_root/preserved-agents"
      fi
    else
      : > "$tmp_root/preserved-agents"
    fi

    {
      if [ -s "$tmp_root/preserved-agents" ]; then
        cat "$tmp_root/preserved-agents"
        printf '\n'
      fi
      cat "$tmp_root/managed-block"
    } > "$tmp_root/new-agents"

    parent=$(dirname -- "$global_agents")
    mkdir -p "$parent"
    staged=$(mktemp "$parent/.codex-agent-config.XXXXXX") || fail "could not stage AGENTS.md"
    cp "$tmp_root/new-agents" "$staged" || { rm -f "$staged"; fail "could not stage AGENTS.md"; }
    mv -f "$staged" "$global_agents" || { rm -f "$staged"; fail "could not install AGENTS.md"; }
    printf '%s\n' 'INSTALLED AGENTS.md managed routing block'
    changed=$((changed + 1))
  fi
fi

if [ "$mode" = check ]; then
  if [ "$failures" -gt 0 ]; then
    printf '%s\n' "ERROR: check failed for $failures managed item(s)" >&2
    exit 1
  fi
  printf '%s\n' "CHECK PASSED: 19 agent profiles, route-subagents, and AGENTS.md match $codex_home"
  exit 0
fi

while IFS= read -r source; do
  name=${source##*/}
  cmp -s "$source" "$codex_home/agents/$name" || fail "final verification failed: agents/$name"
done < "$tmp_root/agents.list"

while IFS= read -r source; do
  relative_inside=${source#"$skill_prefix"}
  cmp -s "$source" "$codex_home/skills/route-subagents/$relative_inside" || fail "final verification failed: skills/route-subagents/$relative_inside"
done < "$tmp_root/skill.list"

awk -v begin="$begin_marker" -v end="$end_marker" '
  { line=$0; sub(/\r$/, "", line) }
  line == begin { inside=1 }
  inside { print }
  line == end { inside=0; found=1 }
  END { if (!found) exit 2 }
' "$global_agents" | sed 's/\r$//' > "$tmp_root/final-block"
cmp -s "$tmp_root/managed-block" "$tmp_root/final-block" || fail "final verification failed: AGENTS.md managed routing block"

printf '%s\n' "INSTALL PASSED: $changed managed item(s) updated in $codex_home"
if [ -n "$backup_root" ]; then
  printf '%s\n' "BACKUP: $backup_root"
fi
printf '%s\n' 'Restart Codex and start a new task to load the custom-agent types.'
