const fs = require("fs");
const path = require("path");

const root = "D:\\电子规范";

// Known standard name mappings for code-only files
const nameMap = {
  "GB 50289-2016": "城市工程管线综合规划规范",
  "GB 50688-2011": "城市道路交通设施设计规范",
  "GB 50763-2012": "无障碍设计规范",
  "JTG 3450-2019": "公路路基路面现场测试规程",
  "JTG B 05-2015": "公路护栏安全性能评价标准",
  "JTG D 30-2015": "公路路基设计规范",
  "JTG D 61-2005": "公路圬工桥涵设计规范",
  "JTG D 63-2007": "公路桥涵地基与基础设计规范",
  "JTG E 30-2005": "公路工程水泥及水泥混凝土试验规程",
  "JTG E 60-2008": "公路路基路面现场测试规程",
  "CJJ 11-2011": "城市桥梁设计规范",
  "CJJ 194-2013": "城市道路路基设计规范",
  "CJJ 221-2015": "城市地下道路工程设计规范",
  "CJJ 56-2012": "市政工程勘察规范",
  "CJJ 69-1995": "城市人行天桥与人行地道技术规范"
};

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
let failed = 0;

for (const f of allFiles) {
  const ext = path.extname(f.name);
  const base = path.basename(f.name, ext).trim();
  
  if (nameMap[base]) {
    const newName = nameMap[base] + " (" + base + ")" + ext;
    const newPath = path.join(f.dir, newName);
    
    try {
      fs.renameSync(f.fullPath, newPath);
      renamed++;
      console.log("  ✓ " + f.name + "  ->  " + newName);
    } catch (e) {
      failed++;
      console.log("  ✗ " + f.name + " -> " + e.message);
    }
  }
}

console.log("\n完成: " + renamed + " 个重命名, 失败: " + failed);
