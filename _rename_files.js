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

function hasCode(name) {
  const upper = name.toUpperCase();
  return /(?:GB|GB\/T|GBJ|JTJ|JTG|CJJ|CJ\/T|JGJ|SL|DL|NB|DB\d{2}\/|DBJ|DGJ|AASHTO|ASTM|BS\s*\d|EN\s*\d|ISO\s*\d|DIN|ACI|FIDIC)\s*[A-Z\/]?\s*\d/.test(upper);
}

function normalizeName(name) {
  let n = name.replace(/_\d+(?=\.\w+$)/, "");
  n = n.replace(/\([^)]*\d{3,}[^)]*\)/g, "");
  n = n.replace(/\s+/g, " ").trim();
  return n;
}

// Build code map from files that HAVE codes
const codeMap = {};
for (const f of allFiles) {
  if (hasCode(f.name)) {
    const base = normalizeName(f.name);
    const upper = f.name.toUpperCase();
    const m = upper.match(/((?:GB|GB\/T|GBJ|JTJ|JTG|CJJ|CJ\/T|JGJ|SL|DL|NB|DB\d{2}\/|DBJ|DGJ|AASHTO|ASTM|BS|EN|ISO|DIN|ACI|FIDIC)\s*[A-Z\/]?\s*\d{1,5}(?:-\d{4})?)/);
    if (m) {
      if (!codeMap[base]) codeMap[base] = new Set();
      codeMap[base].add(m[1].trim());
    }
  }
}

// Rename files without codes
let renamed = 0;
let failed = 0;

for (const f of allFiles) {
  if (hasCode(f.name)) continue;
  if (/\.(exe|url|js|css|gif|json|csv|bak|mp4|mp3|wps|png|jpg|JPG|jpeg|dwg|htm|ppt|chw)$/i.test(f.name)) continue;
  if (f.name.length < 5) continue;
  
  const base = normalizeName(f.name);
  if (codeMap[base] && codeMap[base].size > 0) {
    const code = [...codeMap[base]][0];
    const ext = path.extname(f.name);
    let baseName = path.basename(f.name, ext);
    const newName = baseName + " (" + code + ")" + ext;
    const newPath = path.join(f.dir, newName);
    
    try {
      fs.renameSync(f.fullPath, newPath);
      renamed++;
      console.log("  ✓ " + f.name + " -> " + newName);
    } catch (e) {
      failed++;
      console.log("  ✗ " + f.name + " -> " + e.message);
    }
  }
}

console.log("\n=== 完成 ===");
console.log("成功重命名: " + renamed + " 个文件");
console.log("失败: " + failed + " 个文件");
