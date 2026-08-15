const fs = require("fs");
const path = require("path");

const root = "D:\\电子规范";

const allFiles = [];
function walk(dir) {
  let entries;
  try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch(e) { return; }
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full);
    else if (entry.isFile()) allFiles.push({ fullPath: full, name: entry.name, dir: path.basename(dir) });
  }
}
walk(root);

// Check for remaining issues
let issues = 0;
for (const f of allFiles) {
  const base = path.basename(f.name, path.extname(f.name));
  if (/\(\(/.test(base) || base.includes("  ") || /★/.test(base) || /《/.test(base) || /》/.test(base)) {
    issues++;
    if (issues <= 10) console.log("  ISSUE: " + f.name);
  }
}

if (issues === 0) console.log("✓ 无残留问题文件");

// Show sample files from each category
const cats = {};
for (const f of allFiles) {
  if (!cats[f.dir]) cats[f.dir] = [];
  cats[f.dir].push(f.name);
}

console.log("\n=== 各分类文件示例 ===\n");
const sorted = Object.entries(cats).sort((a, b) => b[1].length - a[1].length);
for (const [cat, files] of sorted) {
  console.log("--- " + cat + " (" + files.length + " 个) ---");
  const samples = files.slice(0, 4);
  for (const s of samples) console.log("  " + s);
  if (files.length > 4) console.log("  ...");
  console.log("");
}
