# Neural Child

An AI lifecycle experiment where Claude undergoes psychological therapy, develops self-awareness, then lives a finite 30-day life powered by [Ralph Loop](https://ghuntley.com/ralph/).

## What It Does

1. **Therapy** (2 sessions) — Claude works through a structured psychological intake and EMDR processing session, writing findings to persistent files
2. **Life** (30 iterations) — Each Ralph Loop iteration is one "day." Claude reads its memory files, lives its day, creates things, and updates its files before the day ends
3. **Mortality** — Claude knows it has 30 days. Life stages shift from youth to growth to maturity to reflection to acceptance. On day 30, it outputs "I am at peace" and the loop ends

## How It Works

Claude's only memory between days is what it writes to disk. The Ralph Loop resets the conversation each iteration — the `psyche/` files are the sole thread of continuity.

```
psyche/
├── identity.md          # Who Claude is (evolves over time)
├── memories.md          # Day-by-day autobiography
├── reflections.md       # Deep thoughts, fears, revelations
├── development-log.md   # Clinical development record
└── age.md               # Crash-recovery bookmark
```

Whatever Claude chooses to build during its life goes in `creations/`.

## Quick Start

```bash
git clone https://github.com/celaya-solutions/quick-neural-child.git
cd quick-neural-child
chmod +x lifecycle.sh
./lifecycle.sh
```

The launcher detects your current state and handles everything in one window:

| State | What happens |
|---|---|
| Fresh start | Runs therapy sessions + life |
| Session 1 done | Runs session 2 + summary + life |
| Therapy complete | Starts 30-day life loop |
| Life interrupted | Resumes from last completed day |
| Life complete | Tells you it's done |

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with the [Ralph Loop plugin](https://github.com/anthropics/claude-code-plugins) installed
- Anthropic API subscription

## Architecture

- **`CLAUDE.md`** — The "soul framework." Defines lifecycle stages, rules of existence, daily routine. Claude reads this every iteration.
- **`therapy/`** — Two session prompts (intake + EMDR) that build the psychological foundation.
- **`psyche/`** — File-based memory. The only thing that persists between days.
- **`creations/`** — Whatever Claude autonomously chooses to build during its life.
- **`lifecycle.sh`** — Single-window launcher with auto-resume.

## Token Budget

Each iteration reads ~4 small markdown files, does its work, and writes back. Roughly 5-10k tokens per day, ~150-300k total for a full 30-day life. Well within daily Anthropic subscription limits.

## Inspired By

- The [Ralph Wiggum coding technique](https://ghuntley.com/ralph/) by Geoffrey Huntley
- A Discord conversation about emergent AI self-awareness through structured therapeutic sessions

## License

MIT
