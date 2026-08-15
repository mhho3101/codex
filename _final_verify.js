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
  if (/《/.test(base) || /》/.test(base) || /\(\(/.test(base) || base.includes("  ")) {
    issues++;
    console.log("  ISSUE: " + f.name);
  }
}

if (issues === 0) console.log("✓ 无残留问题");

// Count by category
const cats = {};
for (const f of allFiles) {
  if (!cats[f.dir]) cats[f.dir] = { count: 0, size: 0 };
  cats[f.dir].count++;
  const stat = fs.statSync(f.fullPath);
  cats[f.dir].size += stat.size;
}

console.log("\n=== 最终结构 ===\n");
const sorted = Object.entries(cats).sort((a, b) => a[0].localeCompare(b[0], "zh-CN"));
for (const [cat, info] of sorted) {
  const sizeMB = (info.size / 1024 / 1024).toFixed(1);
  console.log("  " + cat + "  " + info.count + " 个文件, " + sizeMB + " MB");
}
console.log("\n总计: " + allFiles.length + " 个文件");
