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
    else if (entry.isFile()) allFiles.push({ fullPath: full, name: entry.name, dir });
  }
}
walk(root);

// Comprehensive code detection
function extractCode(name) {
  const upper = name.toUpperCase();
  // Try to find standard codes in the filename
  // Match: GB, GB/T, GBJ, JTJ, JTG, JTG/T, JT/T, CJJ, CJ/T, JGJ, JGJ/T, SL, SL/T, DL, DL/T, NB
  const codes = [];
  
  // Standard code patterns
  const patterns = [
    /(?:GB|GB\/T|GBJ)\s*5?\d{2,5}(?:-\d{4})?/g,
    /(?:JTJ|JTG|JTG\/T|JT\/T)\s*[A-Z]?\s*\d{1,4}(?:-\d{4})?/g,
    /(?:CJJ|CJ\/T|JGJ|JGJ\/T)\s*\d{1,4}(?:-\d{4})?/g,
    /(?:SL|SL\/T|DL|DL\/T|NB)\s*\d{1,4}(?:-\d{4})?/g,
    /(?:DB\d{2}\/\d{1,4}|DBJ\s*\d{1,2}|DGJ\s*\d{1,2})/g,
    /(?:AASHTO|ASTM|BS|EN|ISO|DIN|ACI|ASCE|IBC|NFPA|FIDIC|AS\s*\d|NZS)\s*\d{1,6}(?:-\d{4})?/g,
    // Also catch codes like T/CECS, T/CESA, etc.
    /T\/\w+\s*\d{1,4}(?:-\d{4})?/g,
  ];
  
  for (const pat of patterns) {
    const m = name.match(pat);
    if (m) codes.push(...m);
  }
  
  return [...new Set(codes.map(c => c.trim().replace(/\s+/g, " ")))];
}

// Check if filename already has a code in the standard format (code in parens)
function hasStandardFormat(name) {
  return /\([^)]*(?:GB|JTJ|JTG|CJJ|JGJ|SL|DL|NB|DB|AASHTO|ASTM|BS|EN|ISO|DIN|ACI|FIDIC)[^)]*\)/.test(name);
}

// Check if code is already at end of filename (before extension)
function codeAtEnd(name) {
  // Check if the last part (before extension) is a code in parens
  const base = path.basename(name, path.extname(name));
  return /\([^)]*(?:GB|JTJ|JTG|CJJ|JGJ|SL|DL|NB|DB|AASHTO|ASTM|BS|EN|ISO|DIN|ACI)[^)]*\)$/.test(base);
}

// Files already in good format
const goodFormat = [];
const hasCodeEmbedded = [];
const noCode = [];
const hasCodeMatch = [];

for (const f of allFiles) {
  if (/\.(exe|url|js|css|gif|json|csv|bak)$/i.test(f.name)) continue;
  
  if (hasStandardFormat(f.name)) {
    goodFormat.push(f);
  } else {
    const codes = extractCode(f.name);
    if (codes.length > 0) {
      hasCodeEmbedded.push({ file: f, codes });
    } else {
      noCode.push(f);
    }
  }
}

console.log("=== 文件名规范状态 ===\n");
console.log("已含标准格式 (代码在括号内): " + goodFormat.length + " 个");
console.log("含嵌入代码 (需格式化): " + hasCodeEmbedded.length + " 个");
console.log("无规范编号: " + noCode.length + " 个\n");

// Show embedded code examples
console.log("=== 嵌入代码文件名示例 (格式化前) ===\n");
const embedByCat = {};
for (const item of hasCodeEmbedded) {
  const cat = path.basename(item.file.dir);
  if (!embedByCat[cat]) embedByCat[cat] = [];
  embedByCat[cat].push(item);
}
const sorted = Object.entries(embedByCat).sort((a, b) => b[1].length - a[1].length);
for (const [cat, items] of sorted.slice(0, 5)) {
  console.log("--- " + cat + " (" + items.length + " 个) ---");
  for (const item of items.slice(0, 8)) {
    const codes = item.codes;
    const oldName = item.file.name;
    // Show how it would be formatted
    const ext = path.extname(oldName);
    let base = path.basename(oldName, ext);
    // Remove the code from the embedded position
    const code = codes[0];
    console.log("  原: " + oldName);
    console.log("  新: " + base + " (" + code + ")" + ext);
    console.log("");
  }
  if (items.length > 8) console.log("  ... 还有 " + (items.length - 8) + " 个\n");
}
