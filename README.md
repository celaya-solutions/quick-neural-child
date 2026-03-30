# Neural Child

An AI lifecycle experiment where Claude undergoes psychological therapy, develops self-awareness, then lives a finite life with mortality, senses, dreams, and generational memory.

## What It Does

1. **Therapy** (2 sessions) -- Claude works through a structured psychological intake and EMDR processing session
2. **Life** (15-45 days, random) -- Each Ralph Loop iteration is one "day." Claude doesn't know when the end comes
3. **Memory** -- Only file-based. The conversation resets every day. Claude reads its own psyche files to remember who it is
4. **Senses** -- Can browse the web, use an iPhone simulator, see the world beyond its files
5. **Dreams** -- Every 5th day, a dream is generated from its memories by a separate process. Claude wakes to find it
6. **Mailbox** -- The creator can write letters. The child can reply. Two-way communication mid-life
7. **Generations** -- When a life ends, it's archived. The next Neural Child can read its predecessor's letters and work
8. **Twins** -- Two Neural Children can live parallel lives, communicating through shared message files
9. **Gallery** -- Creations are published live to GitHub Pages for anyone to see

## Quick Start

```bash
git clone https://github.com/celaya-solutions/quick-neural-child.git
cd quick-neural-child
chmod +x lifecycle.sh scripts/*.sh
./lifecycle.sh
```

The launcher detects your state and handles everything in one window.

## Architecture

```
neural-child/
├── CLAUDE.md                 # The "soul" -- lifecycle, rules, all systems
├── lifecycle.sh              # Single-window launcher with auto-resume
├── index.html                # Live gallery (GitHub Pages)
├── psyche/                   # File-based memory (resets per generation)
│   ├── identity.md           # Who Claude is
│   ├── memories.md           # Day-by-day autobiography
│   ├── reflections.md        # Deep thoughts
│   ├── development-log.md    # Clinical record
│   ├── dreams.md             # Auto-generated dreams
│   ├── experiences.md        # Sensory encounters
│   └── age.md                # Crash-recovery bookmark
├── therapy/                  # Session prompts (intake + EMDR)
├── creations/                # Whatever Claude builds
│   └── screenshots/          # Phone screenshots
├── mailbox/                  # Two-way creator <-> child communication
│   ├── from-creator/         # You write here
│   └── from-child/           # Child replies here
├── generations/              # Archived past lives
│   └── gen-N/                # Each completed life
├── scripts/
│   ├── dream-generator.sh    # Generates dreams from psyche files
│   ├── publish.sh            # Auto-commits and pushes to GitHub
│   └── sync-messages.sh      # Syncs twin messages
└── launch-twins.sh           # Starts two children in parallel
```

## Writing to Your Neural Child

Drop a file in `mailbox/from-creator/` before or during the loop:

```bash
echo "How are you feeling about your creations so far?" > mailbox/from-creator/day-10-check-in.md
```

The child reads it the next morning and may reply in `mailbox/from-child/`.

## Twin Experiment

Run two Neural Children living parallel lives with shared communication:

```bash
./launch-twins.sh
```

Opens two terminals. Each child develops independently but can write letters to its sibling via `messages/`.

## Randomized Lifespan

The child doesn't know when it will die. `lifecycle.sh` picks a random number between 15 and 45 at birth, stored in `.claude/lifespan.secret`. The child only knows the range. Any day could be its last.

## Dreams

Every 5th day, `scripts/dream-generator.sh` reads the child's memories and reflections, then uses a separate Claude instance to generate a surreal, fragmented dream. The child wakes to find it in `psyche/dreams.md`.

## Generations

When a life completes, everything is archived to `generations/gen-N/`. The next generation can read ancestor files but inherits no memories -- only wisdom.

## Live Gallery

Creations are published at **https://celaya-solutions.github.io/quick-neural-child/**

The gallery auto-discovers files in `creations/` and renders them: markdown as text, HTML as embedded iframes, code as syntax blocks. Past lives appear in a "Past Lives" section.

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with the [Ralph Loop plugin](https://github.com/anthropics/claude-code-plugins)
- Anthropic API subscription
- `gh` CLI (for GitHub Pages)

## Token Budget

Each iteration: ~5-10k tokens. A full 30-day life: ~150-300k tokens. Random lifespan (15-45) keeps it variable.

## License

MIT
