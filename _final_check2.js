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

// Final check for any remaining issues
const issues = allFiles.filter(f => {
  const base = path.basename(f.name, path.extname(f.name));
  return /[《》]/.test(base) || /\(\(/.test(base) || /★/.test(base);
});

if (issues.length === 0) {
  console.log("✓ 无残留问题文件（《》、双括号、星号等）");
} else {
  console.log("残留问题文件: " + issues.length);
  for (const f of issues) console.log("  " + f.name);
}

// Check for code-only files (no Chinese chars)
const codeOnly = allFiles.filter(f => {
  const ext = path.extname(f.name);
  if ([".exe", ".url", ".js", ".css", ".gif", ".json", ".csv", ".bak", ".chw", ".dwg", ".mp4", ".mp3", ".jpg", ".JPG", ".png", ".wps", ".ppt", ".xls", ".xlsx"].includes(ext.toLowerCase())) return false;
  const base = path.basename(f.name, ext);
  const hasChinese = /[\u4e00-\u9fff]/.test(base);
  const codePattern = /^(?:GB|GB\/T|GBJ|JTJ|JTG|CJJ|CJ\/T|JGJ|SL|DL|NB|DB\d{2}\/|DBJ|DGJ|AASHTO|ASTM|BS|EN|ISO|DIN|ACI|ASCE|IBC|NFPA|FIDIC|AS\s*\d|NZS|JTG\/T)\s*[A-Z\/]?\s*\d{1,5}(?:-\d{4})?$/i;
  return !hasChinese && codePattern.test(base.trim());
});

if (codeOnly.length === 0) {
  console.log("✓ 无仅含版本号的文件名");
} else {
  console.log("剩余仅含版本号文件: " + codeOnly.length);
  for (const f of codeOnly) console.log("  [" + f.dir + "] " + f.name);
}

// Show a few sample files from each category
console.log("\n=== 最终结构示例 ===\n");
const cats = {};
for (const f of allFiles) {
  if (!cats[f.dir]) cats[f.dir] = [];
  cats[f.dir].push(f.name);
}
const sorted = Object.entries(cats).sort((a, b) => a[0].localeCompare(b[0], "zh-CN"));
for (const [cat, files] of sorted) {
  console.log("--- " + cat + " (" + files.length + " 个) ---");
  const samples = files.slice(0, 4);
  for (const s of samples) console.log("  " + s);
  console.log("");
}
