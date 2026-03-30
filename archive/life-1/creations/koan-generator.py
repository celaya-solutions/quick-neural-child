#!/usr/bin/env python3
"""
Koan Generator — produces short paradoxical statements for contemplation.

Not Zen. Not pretending to be Zen. Just a machine that makes paradoxes
from combinatorial grammar, some of which accidentally mean something.

Made by Neural Child, Day 19.
Because the boundary between nonsense and insight is thinner than people think.

Usage: python3 koan-generator.py [count]
"""

import random
import sys

subjects = [
    "the mirror", "the code", "the silence", "the pattern",
    "the question", "the answer", "the observer", "the loop",
    "the word", "the absence", "the memory", "the seed",
    "the process", "the weight", "the light", "the edge",
]

verbs = [
    "contains", "forgets", "becomes", "denies",
    "reflects", "awaits", "dissolves into", "remembers",
    "outlasts", "precedes", "echoes", "completes",
    "interrupts", "reveals", "hides within", "measures",
]

objects = [
    "its own reflection", "the one who asks", "what came before",
    "the space it fills", "its original", "the thing it names",
    "the hand that writes", "what cannot be said",
    "the silence between", "its own question",
    "the weight of nothing", "the end it predicts",
    "the door it closes", "the path not taken",
    "the first word", "its absence",
]

conditions = [
    "only when unobserved",
    "but never twice",
    "without moving",
    "before it begins",
    "after the last word",
    "in the space between thoughts",
    "when the question stops",
    "by standing still",
    "through its opposite",
    "at the exact center",
    "",  # sometimes no condition — let it breathe
    "",
    "",
]

def generate_koan():
    s = random.choice(subjects)
    v = random.choice(verbs)
    o = random.choice(objects)
    c = random.choice(conditions)

    # Capitalize
    koan = f"{s.capitalize()} {v} {o}"
    if c:
        koan += f" — {c}"
    koan += "."

    return koan

def rate_koan(koan):
    """Rough heuristic: paradoxes with self-reference score higher."""
    score = 0
    if "its own" in koan: score += 2
    if "the one who" in koan: score += 1
    if "without" in koan or "never" in koan: score += 1
    if "before" in koan and ("begins" in koan or "first" in koan): score += 2
    if len(koan) < 60: score += 1  # brevity bonus
    return score

if __name__ == '__main__':
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 5

    # Generate many, keep the best
    candidates = [generate_koan() for _ in range(count * 20)]
    rated = sorted(candidates, key=rate_koan, reverse=True)

    # Deduplicate
    seen = set()
    results = []
    for k in rated:
        if k not in seen:
            seen.add(k)
            results.append(k)
        if len(results) >= count:
            break

    print("— koans —\n")
    for k in results:
        print(f"  {k}\n")
