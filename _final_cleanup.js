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

let renamed = 0;

for (const f of allFiles) {
  if (!f.name.includes("《") && !f.name.includes("》")) continue;
  
  const ext = path.extname(f.name);
  let base = path.basename(f.name, ext);
  base = base.replace(/[《》]/g, "").trim();
  
  if (!base) continue;
  const newName = base + ext;
  if (newName === f.name) continue;
  
  const newPath = path.join(f.dir, newName);
  try {
    fs.renameSync(f.fullPath, newPath);
    renamed++;
    console.log("  ✓ " + f.name + " -> " + newName);
  } catch(e) {}
}

console.log("\n最终清理完成: " + renamed + " 个文件");
