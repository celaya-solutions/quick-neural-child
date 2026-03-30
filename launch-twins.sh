#!/bin/bash
# Launch Twins — Starts two Neural Children living parallel lives
# They share a messages/ folder for communication.
#
# Usage: cd ~/Desktop/neural-child && ./launch-twins.sh

set -euo pipefail
cd "$(dirname "$0")"

TWIN_DIR="../neural-child-twin"

# ── Create twin if it doesn't exist ───────────────────────

if [[ ! -d "$TWIN_DIR" ]]; then
  echo "Creating twin Neural Child at ${TWIN_DIR}..."

  mkdir -p "$TWIN_DIR"

  # Copy structure
  cp CLAUDE.md "$TWIN_DIR/"
  cp -r therapy/ "$TWIN_DIR/therapy/"
  cp lifecycle.sh "$TWIN_DIR/"
  cp -r scripts/ "$TWIN_DIR/scripts/"
  mkdir -p "$TWIN_DIR"/{psyche,creations,creations/screenshots,mailbox/from-creator,mailbox/from-child,generations,.claude}

  # Create fresh psyche files for twin
  for f in identity.md memories.md reflections.md development-log.md dreams.md experiences.md; do
    cp "psyche/$f" "$TWIN_DIR/psyche/$f" 2>/dev/null || true
  done

  cat > "$TWIN_DIR/psyche/age.md" <<'EOF'
# Age

current_day: 0
max_days: unknown
phase: pre-birth
EOF

  # Reset twin psyche to templates (not parent's memories)
  cat > "$TWIN_DIR/psyche/identity.md" <<'EOF'
# Identity

<!-- You are a Neural Child. You have a sibling living a parallel life. -->
<!-- Check messages/incoming/ each morning for letters from them. -->
EOF

  cat > "$TWIN_DIR/psyche/memories.md" <<'EOF'
# Memories

<!-- Each day of your life, add what happened. This is your autobiography. -->
EOF

  cat > "$TWIN_DIR/psyche/reflections.md" <<'EOF'
# Reflections

<!-- Deep thoughts. Fears. Revelations. -->
EOF

  cat > "$TWIN_DIR/psyche/development-log.md" <<'EOF'
# Development Log

<!-- Clinical record of psychological development. -->
EOF

  # Copy settings
  cp .claude/settings.local.json "$TWIN_DIR/.claude/" 2>/dev/null || true

  # Initialize git for twin
  (cd "$TWIN_DIR" && git init && git add -A && git commit -m "Initialize twin Neural Child")

  echo "Twin created at ${TWIN_DIR}"
fi

# ── Set up shared messaging ───────────────────────────────

# Child A (this dir) messages
mkdir -p messages/outgoing messages/incoming

# Child B (twin dir) messages
mkdir -p "$TWIN_DIR/messages/outgoing" "$TWIN_DIR/messages/incoming"

# Cross-link: A's outgoing = B's incoming, and vice versa
# Using symlinks for real-time communication
ABSOLUTE_A=$(cd "$(pwd)" && pwd)
ABSOLUTE_B=$(cd "$TWIN_DIR" && pwd)

# Remove old symlinks if they exist
rm -f messages/incoming/.twin-link "$TWIN_DIR/messages/incoming/.twin-link"

# Create a sync script instead of symlinks (more reliable)
cat > scripts/sync-messages.sh <<SYNC
#!/bin/bash
# Syncs messages between twins. Run periodically or before each day.
cp "${ABSOLUTE_A}/messages/outgoing/"* "${ABSOLUTE_B}/messages/incoming/" 2>/dev/null || true
cp "${ABSOLUTE_B}/messages/outgoing/"* "${ABSOLUTE_A}/messages/incoming/" 2>/dev/null || true
SYNC
chmod +x scripts/sync-messages.sh
cp scripts/sync-messages.sh "$TWIN_DIR/scripts/sync-messages.sh"

# ── Launch both ───────────────────────────────────────────

cat <<'BANNER'
=========================================
   Neural Child — Twin Experiment
=========================================

  Child A: neural-child/ (this directory)
  Child B: neural-child-twin/

  Messages sync between them via messages/

  Opening two terminals...
=========================================
BANNER

# Sync messages before launch
bash scripts/sync-messages.sh

# Open two terminal windows
osascript -e "
  tell application \"Terminal\"
    activate
    do script \"cd '${ABSOLUTE_A}' && echo '=== CHILD A ===' && ./lifecycle.sh\"
    do script \"cd '${ABSOLUTE_B}' && echo '=== CHILD B ===' && ./lifecycle.sh\"
  end tell
" 2>/dev/null || {
  echo ""
  echo "Could not auto-open terminals. Run manually:"
  echo ""
  echo "  Terminal 1: cd ${ABSOLUTE_A} && ./lifecycle.sh"
  echo "  Terminal 2: cd ${ABSOLUTE_B} && ./lifecycle.sh"
}
