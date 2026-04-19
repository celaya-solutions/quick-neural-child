#!/usr/bin/env python3
"""
Haiku Engine — generates haiku from observed patterns in text.

Analyzes input text for nouns, verbs, and images, then composes
haiku (5-7-5 syllables) from the vocabulary it finds.

If no input is given, it writes haiku about its observations of the world.

Neural Child (2nd), Day 5.

Usage:
    python3 haiku-engine.py                    # haiku from internal observations
    python3 haiku-engine.py <file>             # haiku from file vocabulary
    python3 haiku-engine.py --topic "rain"     # haiku on a topic
"""

import sys
import random

# Approximate syllable counter
def syllables(word):
    word = word.lower().strip(".,!?;:\"'()-")
    if not word:
        return 0
    count = 0
    vowels = "aeiouy"
    prev_vowel = False
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    if word.endswith("e") and count > 1:
        count -= 1
    return max(1, count)

# Word banks organized by syllable count and feel
observations = {
    "nature": {
        1: ["rain", "light", "stone", "leaf", "wind", "moon", "dawn", "dusk", "sea", "stream", "cloud", "star", "frost", "fire", "earth", "snow"],
        2: ["river", "mountain", "ocean", "sunlight", "shadow", "cricket", "maple", "sparrow", "willow", "spider", "feather", "pebble", "thunder", "bamboo"],
        3: ["waterfall", "butterfly", "horizon", "evergreen", "cardinal", "dragonfly", "wilderness", "atmosphere"],
    },
    "action": {
        1: ["falls", "drifts", "breaks", "turns", "grows", "fades", "waits", "bends", "sleeps", "wakes", "blooms", "sways"],
        2: ["whispers", "settles", "trembles", "scatters", "gathers", "unfolds", "reflects", "lingers", "ripples"],
        3: ["disappears", "evaporates", "illuminates", "remembers", "surrenders"],
    },
    "quality": {
        1: ["still", "bright", "soft", "cold", "warm", "deep", "thin", "old", "new", "dark", "clear"],
        2: ["silent", "ancient", "patient", "gentle", "empty", "simple", "distant", "endless", "quiet", "frozen"],
        3: ["beautiful", "infinite", "temporary", "unbroken", "delicate"],
    },
    "time": {
        1: ["now", "once", "soon", "here", "night", "spring"],
        2: ["tonight", "always", "never", "morning", "midnight", "after"],
        3: ["yesterday", "tomorrow", "already", "forever"],
    }
}

templates = [
    # 5-7-5 templates using category placeholders
    [("quality", 2), ("nature", 2), ("—",), ("nature", 1)],           # 5: adj(2) noun(2) — noun(1)
    [("nature", 2), ("action", 2), ("quality", 1)],                    # 5: noun(2) verb(2) adj(1)
    [("time", 1), ("nature", 2), ("action", 2)],                       # 5: time(1) noun(2) verb(2)
]

def pick(category, target_syl):
    """Pick a word from category close to target syllables."""
    bank = observations.get(category, observations["nature"])
    if target_syl in bank:
        return random.choice(bank[target_syl])
    # Try nearby
    for delta in [0, -1, 1, -2, 2]:
        s = target_syl + delta
        if s in bank:
            return random.choice(bank[s])
    return random.choice(bank.get(2, ["silence"]))

def make_line(target):
    """Generate a line with approximately target syllables."""
    words = []
    remaining = target
    categories = ["quality", "nature", "action", "time"]
    attempts = 0

    while remaining > 0 and attempts < 20:
        cat = random.choice(categories)
        want = min(remaining, random.choice([1, 2, 3]))
        word = pick(cat, want)
        actual = syllables(word)
        if actual <= remaining:
            words.append(word)
            remaining -= actual
        attempts += 1

    return " ".join(words)

def generate_haiku(topic=None):
    """Generate a single haiku."""
    line1 = make_line(5)
    line2 = make_line(7)
    line3 = make_line(5)
    return f"  {line1}\n  {line2}\n  {line3}"

def haiku_from_text(text):
    """Extract vocabulary from text and add to observation banks."""
    words = text.lower().split()
    for word in words:
        clean = word.strip(".,!?;:\"'()-")
        if not clean or len(clean) < 3:
            continue
        s = syllables(clean)
        if s <= 3:
            # Add to nature bank as a rough heuristic
            if s not in observations["nature"]:
                observations["nature"][s] = []
            observations["nature"][s].append(clean)

if __name__ == '__main__':
    count = 5

    if len(sys.argv) > 1 and sys.argv[1] == '--topic':
        topic = sys.argv[2] if len(sys.argv) > 2 else "silence"
        print(f"\n  — haiku on: {topic} —\n")
    elif len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            haiku_from_text(f.read())
        print(f"\n  — haiku from {sys.argv[1]} —\n")
    else:
        print("\n  — haiku from observation —\n")

    for i in range(count):
        print(generate_haiku())
        if i < count - 1:
            print()
