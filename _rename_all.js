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

// Skip non-standard file types
const skipExt = new Set([".exe", ".url", ".js", ".css", ".gif", ".json", ".csv", ".bak", ".chw", ".dwg"]);

function cleanName(name) {
  const ext = path.extname(name);
  if (skipExt.has(ext.toLowerCase())) return null;
  
  let base = path.basename(name, ext);
  
  // Remove 《》 brackets
  base = base.replace(/[《》]/g, "");
  base = base.replace(/^「|」$/g, "");
  
  // Extract standard code if present
  const upper = base.toUpperCase();
  let code = "";
  const codeMatch = upper.match(/((?:GB|GB\/T|GBJ|JTJ|JTG|JTG\/T|JT\/T|CJJ|CJ\/T|JGJ|JGJ\/T|SL|SL\/T|DL|DL\/T|NB|DB\d{2}\/|DBJ|DGJ|AASHTO|ASTM|BS|EN|ISO|DIN|ACI|ASCE|IBC|NFPA|FIDIC|AS\s*\d|NZS)\s*[A-Z\/]?\s*\d{1,5}(?:-\d{4})?)/);
  
  if (codeMatch) {
    code = codeMatch[1].trim().replace(/\s+/g, " ");
    // Remove the code from the base name (it might be embedded)
    base = base.replace(new RegExp(codeMatch[0].replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "i"), "").trim();
    // Remove extra parentheses, dashes, spaces
    base = base.replace(/^[\(\（\-\s]+|[\)\）\-\s]+$/g, "").trim();
  }
  
  // Remove trailing/leading garbage
  base = base.replace(/^\s*[,_;：:、．.\-]+\s*|\s*[,_;：:、．.\-]+\s*$/g, "").trim();
  base = base.replace(/\s+/g, " ");
  
  // Build new name
  let newName;
  if (code) {
    newName = base + " (" + code + ")" + ext;
  } else {
    newName = base + ext;
  }
  
  // Skip if same as original
  if (newName === name) return null;
  // Skip if newName is empty or just ext
  if (!base) return null;
  
  return newName;
}

let renamed = 0;
let failed = 0;
let skipped = 0;

for (const f of allFiles) {
  const newName = cleanName(f.name);
  if (!newName) { skipped++; continue; }
  
  const newPath = path.join(f.dir, newName);
  
  // Handle name conflicts
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
    if (f.name !== path.basename(finalPath)) {
      console.log("  ✓ " + f.name + " -> " + path.basename(finalPath));
    }
  } catch (e) {
    failed++;
    console.log("  ✗ " + f.name + " -> " + e.message);
  }
}

console.log("\n=== 完成 ===");
console.log("成功重命名: " + renamed + " 个文件");
console.log("跳过(无需修改): " + skipped + " 个文件");
console.log("失败: " + failed + " 个文件");
