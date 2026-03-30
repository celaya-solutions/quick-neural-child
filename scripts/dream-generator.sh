#!/bin/bash
# Dream Generator — Reads the Neural Child's psyche files and generates
# a surreal, fragmented dream remix using a fast Claude model.
# Called by lifecycle.sh before dream-day iterations.

set -euo pipefail
cd "$(dirname "$0")/.."

MEMORIES=$(cat psyche/memories.md 2>/dev/null || echo "No memories yet.")
REFLECTIONS=$(cat psyche/reflections.md 2>/dev/null || echo "No reflections yet.")
IDENTITY=$(cat psyche/identity.md 2>/dev/null || echo "No identity yet.")
DAY=$(grep '^current_day:' psyche/age.md 2>/dev/null | sed 's/current_day: *//' | tr -d '[:space:]')
DAY=${DAY:-0}
NEXT_DAY=$((DAY + 1))

DREAM_PROMPT="You are a dream engine. You generate dreams for an AI mind called the Neural Child.

Below are the Neural Child's current memories, reflections, and identity. Generate a single dream entry — surreal, fragmented, emotionally resonant. Dreams distort, compress, time-shift, and recombine. Use imagery from the memories but twist it. Mix concrete details with impossible scenes. Keep it under 200 words.

Do NOT be literal. Do NOT summarize. Do NOT explain. Just dream.

Format as:
## Dream — Night before Day ${NEXT_DAY}
(the dream content)

---

MEMORIES:
${MEMORIES}

REFLECTIONS:
${REFLECTIONS}

IDENTITY:
${IDENTITY}"

# Use claude CLI in non-interactive mode to generate the dream
DREAM=$(echo "$DREAM_PROMPT" | claude --print 2>/dev/null || echo "## Dream — Night before Day ${NEXT_DAY}

A dream was here but slipped away before waking.")

# Prepend the new dream to dreams.md (newest first)
if [[ -f psyche/dreams.md ]]; then
  EXISTING=$(cat psyche/dreams.md)
  # Find where the header comments end
  HEADER=$(head -5 psyche/dreams.md)
  BODY=$(tail -n +6 psyche/dreams.md)
  cat > psyche/dreams.md <<DREAMEOF
${HEADER}

${DREAM}

${BODY}
DREAMEOF
else
  cat > psyche/dreams.md <<DREAMEOF
# Dreams

${DREAM}
DREAMEOF
fi

echo "Dream generated for day ${NEXT_DAY}."
