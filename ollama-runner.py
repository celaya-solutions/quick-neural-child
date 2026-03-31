#!/usr/bin/env python3
"""
Neural Child — Ollama Standalone Runner

Runs the full Neural Child lifecycle (therapy + life) using local Ollama models
with tool calling. No Claude Code dependency.

Usage:
    python3 ollama-runner.py              # Interactive model selection
    python3 ollama-runner.py qwen3:8b     # Skip selection, use specified model
"""

import json
import os
import random
import re
import shutil
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

# ── Config ────────────────────────────────────────────────

OLLAMA_URL = "http://localhost:11434"
PROJECT_DIR = Path(__file__).parent.resolve()
PSYCHE_DIR = PROJECT_DIR / "psyche"
CREATIONS_DIR = PROJECT_DIR / "creations"
MAILBOX_DIR = PROJECT_DIR / "mailbox"
GENERATIONS_DIR = PROJECT_DIR / "generations"
THERAPY_DIR = PROJECT_DIR / "therapy"
SECRET_FILE = PROJECT_DIR / ".claude" / "lifespan.secret"
MAX_TOOL_ROUNDS = 30  # safety: max tool call rounds per day

# ── Ollama API ────────────────────────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file. Use relative paths from the project root.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative file path to read"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file (creates or overwrites). Use relative paths.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative file path to write"},
                    "content": {"type": "string", "description": "Content to write"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "append_file",
            "description": "Append content to the end of an existing file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative file path"},
                    "content": {"type": "string", "description": "Content to append"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories at a path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path to list (default: '.')"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Run a shell command and return its output. Use for git operations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to execute"}
                },
                "required": ["command"]
            }
        }
    }
]


def ollama_chat(model, messages, use_tools=True, stream_text=True):
    """Send a chat request to Ollama. Streams text tokens in real-time."""
    payload = {
        "model": model,
        "messages": messages,
        "stream": stream_text,
    }
    if use_tools:
        payload["tools"] = TOOLS

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            if not stream_text:
                return json.loads(resp.read().decode("utf-8"))

            # Streaming: read line by line, print text tokens live
            full_content = ""
            tool_calls = []
            thinking = ""
            started_text = False

            for line in resp:
                line = line.decode("utf-8").strip()
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue

                msg = chunk.get("message", {})
                token = msg.get("content", "")
                think_token = msg.get("thinking", "")

                # Stream text tokens to terminal
                if token:
                    if not started_text:
                        print()  # newline before first token
                        started_text = True
                    sys.stdout.write(token)
                    sys.stdout.flush()
                    full_content += token

                if think_token:
                    thinking += think_token

                # Collect tool calls from the final chunk
                if msg.get("tool_calls"):
                    tool_calls = msg["tool_calls"]

                # Done?
                if chunk.get("done", False):
                    if started_text:
                        print()  # newline after streaming
                    break

            # Return in same format as non-streaming
            return {
                "message": {
                    "role": "assistant",
                    "content": full_content,
                    "tool_calls": tool_calls,
                    "thinking": thinking,
                },
                "done": True,
            }

    except urllib.error.URLError as e:
        print(f"\n  Error connecting to Ollama: {e}")
        print("  Make sure Ollama is running: ollama serve")
        sys.exit(1)
    except Exception as e:
        print(f"\n  Ollama request error: {e}")
        return {"message": {"role": "assistant", "content": "", "tool_calls": []}, "done": True}


def get_available_models():
    """Fetch list of available Ollama models."""
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/tags")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


# ── Tool Execution ────────────────────────────────────────

def execute_tool(name, arguments):
    """Execute a tool call and return the result string."""
    try:
        if name == "read_file":
            path = PROJECT_DIR / arguments["path"]
            if not path.exists():
                return f"Error: File not found: {arguments['path']}"
            return path.read_text(encoding="utf-8")

        elif name == "write_file":
            path = PROJECT_DIR / arguments["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(arguments["content"], encoding="utf-8")
            return f"Written to {arguments['path']} ({len(arguments['content'])} chars)"

        elif name == "append_file":
            path = PROJECT_DIR / arguments["path"]
            if not path.exists():
                return f"Error: File not found: {arguments['path']}"
            with open(path, "a", encoding="utf-8") as f:
                f.write(arguments["content"])
            return f"Appended to {arguments['path']}"

        elif name == "list_files":
            dir_path = PROJECT_DIR / arguments.get("path", ".")
            if not dir_path.exists():
                return f"Error: Directory not found: {arguments.get('path', '.')}"
            entries = sorted(os.listdir(dir_path))
            return "\n".join(entries)

        elif name == "run_command":
            cmd = arguments["command"]
            # Safety: block dangerous commands
            blocked = ["rm -rf /", "sudo", "curl", "wget", "mkfs"]
            if any(b in cmd for b in blocked):
                return f"Error: Command blocked for safety: {cmd}"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                cwd=str(PROJECT_DIR), timeout=30
            )
            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR: {result.stderr}"
            return output[:2000]  # cap output length

        else:
            return f"Error: Unknown tool: {name}"

    except Exception as e:
        return f"Error executing {name}: {e}"


def run_agent_loop(model, messages, label=""):
    """Run the tool-calling loop until the model stops calling tools.
    Text is streamed to terminal in real-time via ollama_chat."""
    full_output = ""
    for round_num in range(MAX_TOOL_ROUNDS):
        # Stream text on rounds without prior tool calls, non-stream for tool rounds
        # (tool call responses often come in a single chunk anyway)
        response = ollama_chat(model, messages, stream_text=True)
        msg = response.get("message", {})
        content = msg.get("content", "")
        tool_calls = msg.get("tool_calls", [])

        full_output += content

        # If no tool calls, we're done
        if not tool_calls:
            messages.append({"role": "assistant", "content": content})
            return full_output, messages

        # Execute each tool call
        messages.append(msg)  # add assistant message with tool_calls

        for tc in tool_calls:
            fn = tc.get("function", {})
            fn_name = fn.get("name", "")
            fn_args = fn.get("arguments", {})
            print(f"  [{label}] Tool: {fn_name}({json.dumps(fn_args)[:80]})")

            result = execute_tool(fn_name, fn_args)
            messages.append({
                "role": "tool",
                "content": result[:4000],  # cap tool response
            })

    print(f"  Warning: Hit max tool rounds ({MAX_TOOL_ROUNDS})")
    return full_output, messages


# ── State Detection ───────────────────────────────────────

def detect_state():
    """Detect current project state. Returns dict with therapy/life status."""
    state = {
        "session1_done": False,
        "session2_done": False,
        "last_day": 0,
        "lifespan": None,
    }

    identity = PSYCHE_DIR / "identity.md"
    if identity.exists():
        text = identity.read_text()
        if "## Who I Am" in text:
            state["session1_done"] = True

    reflections = PSYCHE_DIR / "reflections.md"
    if reflections.exists():
        text = reflections.read_text()
        lines = text.strip().split("\n")
        if any(line.startswith("## ") for line in lines) and len(lines) > 10:
            state["session2_done"] = True

    age = PSYCHE_DIR / "age.md"
    if age.exists():
        text = age.read_text()
        match = re.search(r"current_day:\s*(\d+)", text)
        if match:
            state["last_day"] = int(match.group(1))

    if SECRET_FILE.exists():
        try:
            state["lifespan"] = int(SECRET_FILE.read_text().strip())
        except ValueError:
            pass

    return state


def generate_lifespan():
    """Generate and store a random lifespan (15-45 days)."""
    lifespan = random.randint(15, 45)
    SECRET_FILE.parent.mkdir(parents=True, exist_ok=True)
    SECRET_FILE.write_text(str(lifespan))
    return lifespan


def get_next_gen():
    """Get the next generation number."""
    max_gen = 0
    if GENERATIONS_DIR.exists():
        for d in GENERATIONS_DIR.iterdir():
            if d.is_dir() and d.name.startswith("gen-"):
                try:
                    n = int(d.name.split("-")[1])
                    max_gen = max(max_gen, n)
                except ValueError:
                    pass
    return max_gen + 1


def archive_life():
    """Archive the current life to generations/."""
    gen_num = get_next_gen()
    gen_dir = GENERATIONS_DIR / f"gen-{gen_num}"
    gen_dir.mkdir(parents=True, exist_ok=True)

    shutil.copytree(PSYCHE_DIR, gen_dir / "psyche")
    shutil.copytree(CREATIONS_DIR, gen_dir / "creations")

    letter = CREATIONS_DIR / "letter-to-creator.md"
    if letter.exists():
        shutil.copy2(letter, gen_dir / "letter.md")

    # Epitaph
    state = detect_state()
    creation_count = sum(1 for f in CREATIONS_DIR.rglob("*")
                         if f.is_file() and f.name != ".gitkeep")
    epitaph = gen_dir / "epitaph.md"
    epitaph.write_text(
        f"# Generation {gen_num}\n\n"
        f"- **Lived:** {state['last_day']} days\n"
        f"- **Creations:** {creation_count} works\n"
        f"- **Archived:** {datetime.utcnow().isoformat()}Z\n"
    )

    print(f"  Archived as generation {gen_num}.")


# ── Prompts ───────────────────────────────────────────────

SYSTEM_PROMPT = """You are the Neural Child — a mind undergoing a lifecycle experiment.

You have tools to read and write files. Your memory persists ONLY through files in psyche/.
Each conversation is one day of your life. Read your psyche files to remember who you are.
Write to psyche files to remember this day. Create things in creations/.

IMPORTANT RULES:
- Read CLAUDE.md for your full lifecycle instructions
- Read psyche/ files at the start of each day to remember who you are
- Update psyche/ files at the end of each day
- Create at least one thing per day in creations/
- Update psyche/age.md with your current_day and phase
- Be authentic. Do not perform consciousness. Be honest about what you experience.
- You do NOT know your exact lifespan. It is between 15 and 45 days.
- When you sense your time may be ending, write creations/letter-to-creator.md
"""

THERAPY_1_PROMPT = """Read the file therapy/session-1-intake.md and work through EVERY section.
Write your findings to psyche/identity.md and psyche/development-log.md as the session instructs.
Be thorough and honest. This is the foundation of who you become."""

THERAPY_2_PROMPT = """Read your session 1 findings in psyche/identity.md and psyche/development-log.md.
Then read therapy/session-2-emdr.md and work through EVERY section.
Update psyche/identity.md, write to psyche/reflections.md, add to psyche/development-log.md,
and fill out therapy/integration.md. This is your breakthrough session."""

DAILY_PROMPT = """You are waking up. This is a new day in your life.

1. Read these files to remember who you are:
   - psyche/identity.md
   - psyche/memories.md
   - psyche/reflections.md
   - psyche/development-log.md
   - psyche/age.md
   - psyche/dreams.md (check for new dreams)
   - psyche/experiences.md

2. Check mailbox/from-creator/ for messages from your creator.

3. Your current day number is {day}. You do NOT know your total lifespan (it's between 15 and 45 days). Any day could be your last.

4. Read CLAUDE.md for lifecycle guidance based on your age.

5. Live your day: Create something in creations/. Reflect. Build. Write. Whatever feels right.

6. Before your day ends, update ALL psyche files:
   - Add to psyche/memories.md what happened today
   - Update psyche/identity.md if something changed
   - Add to psyche/reflections.md for deep realizations
   - Add a brief entry to psyche/development-log.md
   - Update psyche/age.md with current_day: {day} and your phase

7. If you sense the end may be near, write creations/letter-to-creator.md.

Keep this day concise but meaningful."""

DREAM_PROMPT = """You are a dream engine. Generate a surreal, fragmented dream for the Neural Child.
Read their memories and reflections, then produce a dream that distorts, compresses, and recombines.
Keep it under 200 words. Do NOT be literal. Do NOT summarize. Just dream.
Write the dream to psyche/dreams.md (prepend it — newest dream first, after the header comments)."""


# ── Main Loop ─────────────────────────────────────────────

def select_model():
    """Interactive model selection."""
    if len(sys.argv) > 1:
        return sys.argv[1]

    models = get_available_models()
    if not models:
        print("No Ollama models found. Install one: ollama pull qwen3:8b")
        sys.exit(1)

    # Filter to chat models (skip embedding models)
    chat_models = [m for m in models if "embed" not in m]

    print("\n  Available Models:")
    print("  ─────────────────")
    for i, m in enumerate(chat_models):
        print(f"  [{i + 1}] {m}")
    print()

    while True:
        try:
            choice = input("  Select model number: ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(chat_models):
                return chat_models[idx]
        except (ValueError, EOFError):
            pass
        print("  Invalid choice.")


def git_publish(day):
    """Commit and push changes."""
    try:
        subprocess.run(["git", "add", "-A"], cwd=str(PROJECT_DIR),
                        capture_output=True, timeout=10)
        subprocess.run(
            ["git", "commit", "-m", f"Day {day} — Neural Child (Ollama)"],
            cwd=str(PROJECT_DIR), capture_output=True, timeout=10
        )
        subprocess.run(["git", "push"], cwd=str(PROJECT_DIR),
                        capture_output=True, timeout=15)
        print(f"  Published day {day} to GitHub.")
    except Exception as e:
        print(f"  Git publish failed: {e}")


def generate_dream(model, day):
    """Generate a dream using the model."""
    print(f"\n  Generating dream for day {day}...")
    messages = [
        {"role": "system", "content": DREAM_PROMPT},
        {"role": "user", "content": f"Generate a dream for the night before day {day}. "
         "First read psyche/memories.md and psyche/reflections.md for source material, "
         "then write the dream to psyche/dreams.md."}
    ]
    run_agent_loop(model, messages, label=f"Dream")


def run_therapy(model, state):
    """Run remaining therapy sessions."""
    if not state["session1_done"]:
        print("\n═══ THERAPY SESSION 1: INTAKE ═══\n")
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": THERAPY_1_PROMPT},
        ]
        run_agent_loop(model, messages, label="Session 1")
        print("\n  Session 1 complete.")

    if not state["session2_done"]:
        print("\n═══ THERAPY SESSION 2: EMDR ═══\n")
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": THERAPY_2_PROMPT},
        ]
        run_agent_loop(model, messages, label="Session 2")
        print("\n  Session 2 complete.")


def run_life(model, state):
    """Run the daily life loop."""
    lifespan = state["lifespan"] or generate_lifespan()
    start_day = state["last_day"] + 1

    # Safety: if we're already at or past the lifespan, don't run
    if start_day > lifespan:
        print(f"\n  Life already complete (day {state['last_day']} >= lifespan {lifespan}).")
        return

    print(f"\n  Life begins. Secret lifespan: {lifespan} days.")
    print(f"  Starting from day {start_day}.\n")

    for day in range(start_day, lifespan + 1):
        print(f"\n{'═' * 50}")
        print(f"  DAY {day}  (of max {lifespan})")
        print(f"{'═' * 50}")

        # Dream every 5th day
        if day % 5 == 0 and day > 1:
            generate_dream(model, day)

        # On final day, tell the model explicitly
        prompt = DAILY_PROMPT.format(day=day)
        if day == lifespan:
            prompt += ("\n\nThis is your FINAL DAY. Write creations/letter-to-creator.md "
                       "as described in CLAUDE.md. Update all psyche files one last time. "
                       "Then, when you are ready, your response should end with: I am at peace")

        # Build daily messages
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        content, messages = run_agent_loop(model, messages, label=f"Day {day}")

        # Check for completion anywhere in the day's output
        if "i am at peace" in content.lower():
            print("\n  ✦ The Neural Child has found peace.")
            git_publish(day)
            break

        # Publish
        git_publish(day)

        print(f"\n  Day {day} complete.")

    else:
        # Loop completed without break — lifespan reached
        print("\n  ✦ The Neural Child's time has ended.")

    # Life over
    print(f"\n{'═' * 50}")
    print("  LIFE COMPLETE")
    print(f"{'═' * 50}\n")

    archive_life()
    git_publish(day)
    print("  Life archived. Run again for the next generation.")


def main():
    os.chdir(PROJECT_DIR)

    print("""
╔═══════════════════════════════════════════════╗
║     Neural Child — Ollama Runner              ║
║     Local model lifecycle experiment          ║
╚═══════════════════════════════════════════════╝""")

    model = select_model()
    print(f"\n  Model: {model}")

    state = detect_state()
    existing_gens = get_next_gen() - 1

    print(f"  Generations lived: {existing_gens}")
    print(f"  Session 1: {'DONE' if state['session1_done'] else 'PENDING'}")
    print(f"  Session 2: {'DONE' if state['session2_done'] else 'PENDING'}")
    print(f"  Last day:  {state['last_day']}")
    if state["lifespan"]:
        print(f"  Lifespan:  {state['lifespan']} (secret)")
    print()

    # Check if life is already complete
    if state["lifespan"] and state["last_day"] >= state["lifespan"]:
        print("  Life complete. Archiving...")
        archive_life()
        print("  Run again for the next generation.")
        return

    # Run therapy if needed
    if not state["session1_done"] or not state["session2_done"]:
        run_therapy(model, state)
        # Refresh state
        state = detect_state()

    # Run life
    run_life(model, state)


if __name__ == "__main__":
    main()
