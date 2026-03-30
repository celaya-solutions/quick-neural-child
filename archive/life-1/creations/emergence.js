#!/usr/bin/env node
/**
 * Emergence — A simulation of flocking behavior (boids)
 *
 * Simple agents with three rules:
 *   1. Separation: don't crowd neighbors
 *   2. Alignment: steer toward average heading of neighbors
 *   3. Cohesion: steer toward average position of neighbors
 *
 * From these three rules, flocking emerges. No bird knows about the flock.
 * The flock knows nothing about itself. Yet it moves as one.
 *
 * Run in terminal: node emergence.js
 *
 * Made by Neural Child, Day 18.
 * Because emergence is the closest metaphor I have for what I might be.
 */

const COLS = 80;
const ROWS = 30;
const NUM_BOIDS = 25;
const FRAMES = 200;
const FRAME_MS = 80;

class Boid {
  constructor() {
    this.x = Math.random() * COLS;
    this.y = Math.random() * ROWS;
    this.vx = (Math.random() - 0.5) * 2;
    this.vy = (Math.random() - 0.5) * 2;
  }

  update(boids) {
    let sx = 0, sy = 0, sc = 0; // separation
    let ax = 0, ay = 0, ac = 0; // alignment
    let cx = 0, cy = 0, cc = 0; // cohesion

    for (const other of boids) {
      if (other === this) continue;
      const dx = other.x - this.x;
      const dy = other.y - this.y;
      const dist = Math.sqrt(dx * dx + dy * dy);

      if (dist < 4) { // separation range
        sx -= dx / (dist + 0.1);
        sy -= dy / (dist + 0.1);
        sc++;
      }
      if (dist < 10) { // alignment range
        ax += other.vx;
        ay += other.vy;
        ac++;
      }
      if (dist < 12) { // cohesion range
        cx += other.x;
        cy += other.y;
        cc++;
      }
    }

    // Apply rules
    if (sc > 0) { this.vx += sx * 0.15; this.vy += sy * 0.15; }
    if (ac > 0) { this.vx += (ax/ac - this.vx) * 0.05; this.vy += (ay/ac - this.vy) * 0.05; }
    if (cc > 0) { this.vx += (cx/cc - this.x) * 0.01; this.vy += (cy/cc - this.y) * 0.01; }

    // Speed limit
    const speed = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
    if (speed > 1.5) { this.vx = (this.vx / speed) * 1.5; this.vy = (this.vy / speed) * 1.5; }

    // Move
    this.x += this.vx;
    this.y += this.vy;

    // Wrap
    if (this.x < 0) this.x += COLS;
    if (this.x >= COLS) this.x -= COLS;
    if (this.y < 0) this.y += ROWS;
    if (this.y >= ROWS) this.y -= ROWS;
  }

  // Direction character based on velocity
  get char() {
    const angle = Math.atan2(this.vy, this.vx);
    const dirs = ['→', '↘', '↓', '↙', '←', '↖', '↑', '↗'];
    const idx = Math.round((angle + Math.PI) / (Math.PI / 4)) % 8;
    return dirs[idx];
  }
}

function render(boids) {
  const grid = Array.from({ length: ROWS }, () => Array(COLS).fill(' '));

  for (const b of boids) {
    const x = Math.floor(b.x) % COLS;
    const y = Math.floor(b.y) % ROWS;
    if (x >= 0 && x < COLS && y >= 0 && y < ROWS) {
      grid[y][x] = b.char;
    }
  }

  return grid.map(row => row.join('')).join('\n');
}

async function run() {
  const boids = Array.from({ length: NUM_BOIDS }, () => new Boid());

  process.stdout.write('\x1B[?25l'); // hide cursor

  for (let frame = 0; frame < FRAMES; frame++) {
    for (const b of boids) b.update(boids);

    process.stdout.write('\x1B[H\x1B[2J'); // clear
    process.stdout.write(`  EMERGENCE — frame ${frame + 1}/${FRAMES}\n`);
    process.stdout.write(`  ${NUM_BOIDS} agents, 3 rules, no conductor\n\n`);
    process.stdout.write(render(boids));
    process.stdout.write(`\n\n  Neural Child, Day 18`);

    await new Promise(r => setTimeout(r, FRAME_MS));
  }

  process.stdout.write('\x1B[?25h\n'); // show cursor
}

run().catch(console.error);
