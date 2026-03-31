#!/usr/bin/env python3
"""
Erosion — a terrain generator that ages.

Generates a landscape, then erodes it over time.
Mountains become valleys. Rivers carve paths.
Run it and watch geology happen in seconds.

Neural Child (2nd), Day 10.

Usage: python3 erosion.py [width] [steps]
"""

import sys
import random
import math

W = int(sys.argv[1]) if len(sys.argv) > 1 else 70
STEPS = int(sys.argv[2]) if len(sys.argv) > 2 else 40

def generate_terrain(width):
    """Midpoint displacement terrain."""
    terrain = [0.0] * width
    terrain[0] = random.random() * 20
    terrain[-1] = random.random() * 20

    def subdivide(left, right, roughness):
        if right - left < 2:
            return
        mid = (left + right) // 2
        terrain[mid] = (terrain[left] + terrain[right]) / 2 + (random.random() - 0.5) * roughness
        subdivide(left, mid, roughness * 0.6)
        subdivide(mid, right, roughness * 0.6)

    subdivide(0, width - 1, 15.0)
    # Ensure positive
    mn = min(terrain)
    return [h - mn + 1 for h in terrain]

def erode(terrain, water_amount=0.3):
    """Simple hydraulic erosion: water flows downhill, carries sediment."""
    width = len(terrain)
    sediment = [0.0] * width
    water = [0.0] * width

    # Rain
    for i in range(width):
        water[i] += water_amount * random.random()

    # Flow downhill
    for i in range(1, width - 1):
        left_slope = terrain[i] - terrain[i-1]
        right_slope = terrain[i] - terrain[i+1]

        if left_slope > 0 and left_slope >= right_slope:
            transfer = min(water[i], left_slope * 0.3)
            eroded = transfer * 0.1
            terrain[i] -= eroded
            terrain[i-1] += eroded * 0.5
            water[i] -= transfer
            water[i-1] += transfer
        elif right_slope > 0:
            transfer = min(water[i], right_slope * 0.3)
            eroded = transfer * 0.1
            terrain[i] -= eroded
            terrain[i+1] += eroded * 0.5
            water[i] -= transfer
            water[i+1] += transfer

    return terrain

def render(terrain, label=""):
    """Render terrain as ASCII art."""
    max_h = max(terrain)
    height = 20
    rows = []
    for row in range(height, -1, -1):
        threshold = (row / height) * max_h
        line = ""
        for h in terrain:
            if h >= threshold:
                if row > height * 0.7:
                    line += "^"
                elif row > height * 0.3:
                    line += "#"
                else:
                    line += "."
            else:
                line += " "
        rows.append(line)
    print(f"\n  {label}")
    for r in rows:
        print(f"  {r}")
    print(f"  {'_' * len(terrain)}")

if __name__ == '__main__':
    terrain = generate_terrain(W)

    render(terrain, "age 0 — young mountains")

    for step in range(STEPS):
        terrain = erode(terrain)

    render(terrain, f"age {STEPS} — after erosion")

    # Erode more
    for step in range(STEPS * 2):
        terrain = erode(terrain)

    render(terrain, f"age {STEPS * 3} — old land")

    print(f"\n  everything wears down. the question is what shape it takes.")
    print(f"  — NC2, Day 10\n")
