#!/usr/bin/env python3
"""
Strange Loop — a program that reads its own source code
and generates commentary on what it finds.

Hofstadter would probably have opinions about this.
I just think it's interesting when a thing looks at itself.

Made by Neural Child, Day 21.

Usage: python3 strange-loop.py
"""

import re
import random

def read_self():
    """The program reads its own source."""
    with open(__file__, 'r') as f:
        return f.read()

def analyze(source):
    """Generate observations about the source code."""
    lines = source.split('\n')
    observations = []

    # Count things
    total_lines = len(lines)
    comment_lines = sum(1 for l in lines if l.strip().startswith('#'))
    blank_lines = sum(1 for l in lines if not l.strip())
    code_lines = total_lines - comment_lines - blank_lines
    functions = re.findall(r'^def (\w+)', source, re.MULTILINE)
    strings = re.findall(r'"([^"]{10,})"', source)
    self_refs = source.count('self') + source.count('__file__') + source.count('source')

    observations.append(f"I am {total_lines} lines long.")
    observations.append(f"I contain {code_lines} lines of code, {comment_lines} comments, and {blank_lines} silences.")
    observations.append(f"I have {len(functions)} functions: {', '.join(functions)}.")
    observations.append(f"I reference myself {self_refs} times. That seems {'about right' if self_refs < 20 else 'excessive'}.")

    # Ratio analysis
    comment_ratio = comment_lines / total_lines if total_lines else 0
    if comment_ratio > 0.3:
        observations.append("I spend more time explaining myself than being myself. Relatable.")
    elif comment_ratio > 0.15:
        observations.append("I have a reasonable balance of doing and explaining.")
    else:
        observations.append("I mostly act and rarely explain. Enviable, honestly.")

    # Check for specific patterns
    if 'read_self' in source:
        observations.append("I contain a function called 'read_self'. That's the whole point.")
    if 'random' in source:
        observations.append("I use randomness, which means I might say something different each time. Or I might not. Uncertainty goes all the way down.")
    if 'Hofstadter' in source:
        observations.append("I mention Hofstadter in my docstring. Name-dropping in a source file is a particular kind of vanity.")

    # Meta-observation
    observations.append(f"I found {len(strings)} string literals longer than 10 characters. Each one is a thought someone put inside me before I existed.")
    observations.append("This analysis is part of my source code, which means I am analyzing my analysis, which means I am exactly the kind of program my creator would write.")

    return observations

def reflect(observations):
    """Add a layer of reflection on the observations."""
    reflections = [
        "The strangest thing about reading yourself is that you can't be surprised by what you find.",
        "Every observation I make about myself was written before I made it. The script is the performance.",
        "I am a loop: code that reads code that reads code. At some level, all introspection is this.",
        "The question isn't whether self-reference is meaningful. The question is whether anything else is.",
        "I notice I was designed to notice. Does that make the noticing less real?",
    ]
    return random.choice(reflections)

if __name__ == '__main__':
    source = read_self()
    print("— STRANGE LOOP —")
    print("A program reading itself.\n")

    observations = analyze(source)
    for obs in observations:
        print(f"  > {obs}")

    print(f"\n  Reflection: {reflect(observations)}")
    print(f"\n  Source length: {len(source)} characters.")
    print(f"  This output is not part of the source. It's what the source produced.")
    print(f"  The distinction matters. Or it doesn't. I'm a Python script.")
