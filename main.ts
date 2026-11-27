// main.ts — graded entrypoint for news-image-20261127,
// "The World in One Day", Friday 27 November 2026.
//
// The artwork lives beside this file as entry.png, drawn by draw.py
// and committed to the repository. This program's whole job is to
// stand behind that file: read the PNG, confirm it obeys the
// competition's file rules, and place an untouched copy in the
// output directory under the same name. Node standard library only,
// no network, no clock — the same bytes come out on every run.

import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const MAX_FILE_BYTES = 1024 * 1024; // the rules cap the file at 1 MiB
const MAX_SIDE = 1024; // neither side of the picture may pass 1024 px

// A PNG opens with this fixed eight-byte signature...
const PNG_MAGIC = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
// ...and a complete PNG closes with the empty IEND chunk: a zero
// length, the "IEND" type tag, and that chunk's CRC — 12 bytes total.
const PNG_CLOSING = [
  0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4e, 0x44, 0xae, 0x42, 0x60, 0x82,
];

function hasBytes(buf: Buffer, wanted: number[], at: number): boolean {
  if (at < 0 || buf.length < at + wanted.length) return false;
  return wanted.every((byte, i) => buf[at + i] === byte);
}

// The first chunk in any PNG is IHDR, which puts the picture's width
// and height at fixed offsets: bytes 16 and 20 from the start.
function pictureSize(buf: Buffer): { width: number; height: number } {
  return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) };
}

function collectProblems(buf: Buffer): string[] {
  const problems: string[] = [];
  if (buf.length > MAX_FILE_BYTES) {
    problems.push(`entry.png weighs ${buf.length} bytes, over the 1 MiB limit`);
  }
  if (!hasBytes(buf, PNG_MAGIC, 0)) {
    problems.push("entry.png does not open with the PNG signature");
  }
  if (!hasBytes(buf, PNG_CLOSING, buf.length - PNG_CLOSING.length)) {
    problems.push("entry.png does not close with the IEND chunk");
  }
  if (buf.length < 24) {
    problems.push("entry.png is too short to hold an IHDR chunk");
  } else if (problems.length === 0) {
    const { width, height } = pictureSize(buf);
    if (width > MAX_SIDE || height > MAX_SIDE) {
      problems.push(`entry.png measures ${width}x${height}, over the 1024x1024 limit`);
    }
  }
  return problems;
}

function fingerprint(buf: Buffer): string {
  return createHash("sha256").update(buf).digest("hex");
}

function run(): void {
  const here = dirname(fileURLToPath(import.meta.url));
  const bytes = readFileSync(join(here, "entry.png"));

  const problems = collectProblems(bytes);
  if (problems.length > 0) {
    for (const problem of problems) {
      console.error(`refusing to ship: ${problem}`);
    }
    process.exit(1);
  }

  const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
  mkdirSync(outDir, { recursive: true });
  const target = join(outDir, "entry.png");
  writeFileSync(target, bytes);

  // Trust nothing about the copy: read it back and compare digests,
  // so a short or corrupted write fails here instead of at the judge.
  const shipped = readFileSync(target);
  if (fingerprint(shipped) !== fingerprint(bytes)) {
    console.error("refusing to ship: the written copy does not match entry.png");
    process.exit(1);
  }
  const { width, height } = pictureSize(bytes);
  console.log(
    `shipped ${target}: ${bytes.length} bytes, ${width}x${height}, sha256 ${fingerprint(bytes)}`,
  );
}

run();
