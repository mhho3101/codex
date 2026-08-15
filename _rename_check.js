const fs = require("fs");
const path = require("path");

const root = "D:\\电子规范";

// Recurse all files
const allFiles = [];
function walk(dir) {
  let entries;
  try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch(e) { return; }
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full);
    else if (entry.isFile()) allFiles.push({ fullPath: full, name: entry.name, dir });
  }
}
walk(root);

// Check if filename has a standard code
function hasCode(name) {
  const upper = name.toUpperCase();
  return /(?:GB|GB\/T|GBJ|JTJ|JTG|CJJ|CJ\/T|JGJ|SL|DL|NB|DB\d{2}\/|DBJ|DGJ|AASHTO|ASTM|BS\s*\d|EN\s*\d|ISO\s*\d|DIN|ACI|FIDIC)\s*[A-Z\/]?\s*\d/.test(upper);
}

// Group by "base name" (name without _2, _3 suffix and without code)
function normalizeName(name) {
  // Remove _2, _3, _4, etc. before extension
  let n = name.replace(/_\d+(?=\.\w+$)/, "");
  // Remove the code in parentheses (XXX-XXXX) 
  n = n.replace(/\([^)]*\d{3,}[^)]*\)/g, "");
  // Remove extra whitespace
  n = n.replace(/\s+/g, " ").trim();
  return n;
}

// Find files THAT HAVE a code, grouped by their normalized name
const codeMap = {};
for (const f of allFiles) {
  if (hasCode(f.name)) {
    const base = normalizeName(f.name);
    // Extract the code
    const upper = f.name.toUpperCase();
    const m = upper.match(/((?:GB|GB\/T|GBJ|JTJ|JTG|CJJ|CJ\/T|JGJ|SL|DL|NB|DB\d{2}\/|DBJ|DGJ|AASHTO|ASTM|BS|EN|ISO|DIN|ACI|FIDIC)\s*[A-Z\/]?\s*\d{1,5}(?:-\d{4})?)/);
    if (m) {
      if (!codeMap[base]) codeMap[base] = new Set();
      codeMap[base].add(m[1].trim());
    }
  }
}

// Find files WITHOUT a code
const noCodeFiles = [];
const canRename = [];
for (const f of allFiles) {
  if (hasCode(f.name)) continue;
  if (/\.(exe|url|js|css|gif|json|csv|mp4|mp3|wps|png|jpg|mdi)$/i.test(f.name)) continue; // skip non-standard files
  noCodeFiles.push(f);
  
  const base = normalizeName(f.name);
  if (codeMap[base]) {
    canRename.push({ file: f, codes: [...codeMap[base]], base });
  }
}

console.log("缺少规范编号的文件数: " + noCodeFiles.length);
console.log("可自动补全的文件数: " + canRename.length + "\n");

// Group by category folder
const catMap = {};
for (const item of canRename) {
  const dir = item.file.dir;
  const cat = path.basename(dir);
  if (!catMap[cat]) catMap[cat] = [];
  catMap[cat].push(item);
}

console.log("=== 可补全文件名 (按分类) ===\n");
const sorted = Object.entries(catMap).sort((a, b) => b[1].length - a[1].length);
for (const [cat, items] of sorted) {
  console.log("--- " + cat + " (" + items.length + " 个) ---");
  for (const item of items.slice(0, 10)) {
    const code = item.codes[0];
    const oldName = item.file.name;
    // Build new name: insert code before extension
    const ext = path.extname(oldName);
    let base = path.basename(oldName, ext);
    // Remove _2, _3 suffix for clean display
    const newName = base + " (" + code + ")" + ext;
    console.log("  " + oldName + "  =>  " + newName);
  }
  if (items.length > 10) console.log("  ... 还有 " + (items.length - 10) + " 个");
  console.log("");
}

// Also show files that CANNOT be auto-renamed
const cannotRename = noCodeFiles.filter(f => !canRename.some(r => r.file.fullPath === f.fullPath));
console.log("=== 无法自动补全的文件 (需人工确认) ===\n");
console.log("共 " + cannotRename.length + " 个文件\n");
const catMap2 = {};
for (const f of cannotRename) {
  const cat = path.basename(f.dir);
  if (!catMap2[cat]) catMap2[cat] = [];
  catMap2[cat].push(f);
}
const sorted2 = Object.entries(catMap2).sort((a, b) => b[1].length - a[1].length);
for (const [cat, items] of sorted2) {
  console.log("--- " + cat + " (" + items.length + " 个) ---");
  for (const item of items.slice(0, 8)) {
    console.log("  " + item.name);
  }
  if (items.length > 8) console.log("  ... 还有 " + (items.length - 8) + " 个");
  console.log("");
}
