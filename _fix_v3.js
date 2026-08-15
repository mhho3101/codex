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

let fixed = 0;
let failed = 0;

for (const f of allFiles) {
  const ext = path.extname(f.name);
  const base = path.basename(f.name, ext);
  
  // Fix: "name ( (code)" -> "name (code)"  
  // Also fix: "name (code)" -> "name (code)" (no change)
  // Also fix: "name (code) " -> "name (code)"
  let newBase = base.replace(/\s*\(\s*\(/g, " (");  // " ( (" -> " ("
  newBase = newBase.replace(/\s*\(\s*\)/g, "");       // remove empty ()
  newBase = newBase.replace(/\s+/g, " ").trim();
  newBase = newBase.replace(/\(\s/g, "(").replace(/\s\)/g, ")");
  
  if (newBase === base) continue;
  
  const newName = newBase + ext;
  if (newName === f.name) continue;
  
  const newPath = path.join(f.dir, newName);
  try {
    fs.renameSync(f.fullPath, newPath);
    fixed++;
    console.log("  ✓ " + f.name + " -> " + newName);
  } catch (e) {
    failed++;
  }
}

console.log("\n修复完成: " + fixed + " 个, 失败: " + failed);
