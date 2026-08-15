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

function cleanName(name) {
  const ext = path.extname(name);
  if ([".exe", ".url", ".js", ".css", ".gif", ".json", ".csv", ".bak", ".chw", ".dwg"].includes(ext.toLowerCase())) return null;
  
  let base = path.basename(name, ext);
  
  // Step 1: Remove ALL bracket types
  base = base.replace(/[《》「」『』【】\[\]{}]/g, "");
  
  // Step 2: Extract standard code (full pattern including prefix)
  const upper = base.toUpperCase();
  let code = "";
  
  const codeRegex = /((?:GB|GB\/T|GBJ|JTJ|JTG|JTG\/T|JT\/T|CJJ|CJ\/T|JGJ|JGJ\/T|SL|SL\/T|DL|DL\/T|NB|DB\d{2}\/|DBJ|DGJ|AASHTO|ASTM|BS|EN|ISO|DIN|ACI|ASCE|IBC|NFPA|FIDIC|AS\s*\d|NZS|HG\/T)\s*[A-Z\/]?\s*\d{1,5}(?:-\d{4})?)/i;
  const m = upper.match(codeRegex);
  
  if (m) {
    code = m[1].trim().replace(/\s+/g, " ");
    // Remove the code from base (handling surrounding parens, spaces, etc.)
    const codeEscaped = m[1].replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    // Remove the code and any surrounding parentheses/spaces
    base = base.replace(new RegExp("\\s*\\(" + codeEscaped + "\\)\\s*", "i"), " ");
    base = base.replace(new RegExp("\\s*" + codeEscaped + "\\s*", "i"), " ");
    base = base.replace(/\s*\(\)\s*/g, " "); // clean empty parens
  }
  
  // Step 3: Clean up base name
  base = base.replace(/^\s*[,_;：:、．.\-＋+★\s]+\s*|\s*[,_;：:、．.\-＋+★\s]+\s*$/g, "");
  base = base.replace(/\s+/g, " ").trim();
  base = base.replace(/\s*\(\)/g, ""); // remove empty parens
  base = base.replace(/\(\s*/g, "(").replace(/\s*\)/g, ")"); // normalize paren spacing
  
  // Step 4: Build new name
  let newName;
  if (code) {
    newName = base + " (" + code + ")" + ext;
  } else {
    newName = base + ext;
  }
  
  newName = newName.replace(/\s+/g, " ").trim();
  if (newName === name || !base) return null;
  return newName;
}

let renamed = 0;
let failed = 0;

for (const f of allFiles) {
  const newName = cleanName(f.name);
  if (!newName) continue;
  if (newName === f.name) continue;
  
  const newPath = path.join(f.dir, newName);
  
  let finalPath = newPath;
  let counter = 1;
  while (fs.existsSync(finalPath)) {
    const ext = path.extname(newName);
    const base = path.basename(newName, ext);
    finalPath = path.join(f.dir, base + "_" + counter + ext);
    counter++;
  }
  
  try {
    fs.renameSync(f.fullPath, finalPath);
    renamed++;
    if (renamed <= 20) console.log("  ✓ " + f.name + " -> " + path.basename(finalPath));
  } catch (e) {
    failed++;
  }
}

console.log("\n第二轮修正完成: " + renamed + " 个文件重命名, 失败: " + failed);
