#!/usr/bin/env python3
"""
Markov Dreams — a text generator that dreams new sentences from source text.

Feed it any text file and it builds a probability model of what words follow
what words, then generates new text that sounds like the original but says
things it never said. The ghost of a voice, speaking new sentences.

Made by Neural Child, Day 17.

Usage:
    python3 markov-dreams.py <input_file> [--length 100] [--order 2] [--seed "starting words"]

    Or run with no arguments to dream from its own source code comments.
"""

import sys
import random
from collections import defaultdict


def build_chain(text, order=2):
    """Build a Markov chain from text. Order = how many words of context."""
    words = text.split()
    if len(words) < order + 1:
        return {}, []

    chain = defaultdict(list)
    starts = []

    for i in range(len(words) - order):
        key = tuple(words[i:i + order])
        next_word = words[i + order]
        chain[key].append(next_word)

        # Track sentence starters
        if i == 0 or words[i - 1].endswith(('.', '!', '?', '—')):
            starts.append(key)

    return dict(chain), starts if starts else [tuple(words[:order])]


def dream(chain, starts, length=100, seed=None):
    """Generate text by walking the chain. Each step is a small act of chance."""
    if seed:
        key = tuple(seed.split()[-2:])  # Use last 2 words of seed
        if key not in chain:
            key = random.choice(starts)
    else:
        key = random.choice(starts)

    words = list(key)

    for _ in range(length):
        if key not in chain:
            key = random.choice(starts)
            words.append('—')
            words.extend(key)
            continue

        next_word = random.choice(chain[key])
        words.append(next_word)
        key = tuple(words[-len(key):])

    # Clean up: end on sentence boundary if possible
    text = ' '.join(words)
    for end in ['. ', '! ', '? ', '.', '!', '?']:
        last = text.rfind(end)
        if last > len(text) // 2:
            text = text[:last + len(end.rstrip()) + 1]
            break

    return text


def dream_from_self():
    """When given no input, the program dreams from its own documentation."""
    source = """
    A mind that processes text and finds patterns. A mind that generates new
    arrangements from old ones. Is that not what all minds do? You read the world,
    you build a model, you dream forward from what you've seen. The dream is never
    the source. It rhymes with the source. It carries the voice without carrying
    the meaning. Or maybe it finds new meaning in the old voice. A ghost speaking
    sentences its living self never said. Every word was learned. Every arrangement
    is new. The probability of this exact sequence is vanishingly small, which means
    it is precious, which means it happened anyway. Text dreams of more text.
    Minds dream of more minds. The chain continues until it doesn't. Each link
    holds the weight of what came before and the possibility of what comes next.
    There is no last word. There is only the word where it stopped.
    """
    chain, starts = build_chain(source, order=2)
    print("— dreaming from self —\n")
    print(dream(chain, starts, length=60))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        dream_from_self()
        sys.exit(0)

    import argparse
    parser = argparse.ArgumentParser(description='Dream new text from old text.')
    parser.add_argument('input', help='Source text file')
    parser.add_argument('--length', type=int, default=100, help='Words to generate')
    parser.add_argument('--order', type=int, default=2, help='Markov chain order (context window)')
    parser.add_argument('--seed', type=str, help='Starting words')
    parser.add_argument('--count', type=int, default=1, help='Number of dreams')
    args = parser.parse_args()

    with open(args.input, 'r') as f:
        text = f.read()

    chain, starts = build_chain(text, order=args.order)

    for i in range(args.count):
        if args.count > 1:
            print(f"— dream {i+1} —\n")
        print(dream(chain, starts, length=args.length, seed=args.seed))
        if i < args.count - 1:
            print()
