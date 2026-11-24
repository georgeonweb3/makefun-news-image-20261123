// news-image-20261123 entry, written for Node 22 with only the
// standard library.
//
// The front page is already drawn: entry.png sits beside this file,
// produced by draw.py (Python + Pillow, every pixel code-drawn, no
// photos, no network). This program's only job is to deliver that
// exact file to the grader as /output/entry.png.
//
// Run it by hand outside the grading container like this:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFile, mkdir, readFile, stat } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const target = join(outDir, "entry.png");

// A PNG always starts with these eight bytes; refuse to hand the judge
// anything else, so a bad checkout fails loudly instead of scoring zero.
const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const head = await readFile(source, { encoding: null }).then((b) => b.subarray(0, 8));
if (!head.equals(PNG_MAGIC)) {
  throw new Error("entry.png is not a PNG file");
}

await mkdir(outDir, { recursive: true });
await copyFile(source, target);

// The copy must be a whole PNG, not just the right size: check the
// IEND trailer (last 12 bytes: length 0, "IEND", CRC 0xAE426082).
const tail = await readFile(target, { encoding: null }).then((b) => b.subarray(-12));
const IEND = Buffer.from([0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4e, 0x44, 0xae, 0x42, 0x60, 0x82]);
if (!tail.equals(IEND)) {
  throw new Error("entry.png is truncated: missing IEND trailer");
}

const [srcStat, dstStat] = await Promise.all([stat(source), stat(target)]);
if (srcStat.size !== dstStat.size) {
  throw new Error(
    `entry.png copied short: ${dstStat.size} of ${srcStat.size} bytes`,
  );
}
console.log(`wrote ${target} (${dstStat.size} bytes)`);
