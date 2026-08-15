const fs = require("fs");

const root = "D:\\电子规范";

const allFiles = [];
function walk(dir) {
  let entries;
  try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch(e) { return; }
  for (const entry of entries) {
    const full = require("path").join(dir, entry.name);
    if (entry.isDirectory()) walk(full);
    else if (entry.isFile()) allFiles.push({ fullPath: full, name: entry.name });
  }
}
walk(root);

const codes = [
  "GB 50289-2016", "GB 50688-2011", "GB 50763-2012",
  "JTG 3450-2019", "JTG B 05-2015", "JTG D 30-2015", "JTG D 61-2005", "JTG D 63-2007", "JTG E 30-2005", "JTG E 60-2008",
  "CJJ 11-2011", "CJJ 194-2013", "CJJ 221-2015", "CJJ 56-2012", "CJJ 69-1995",
  "AS 1743-2001", "AS 1744-1975"
];

for (const code of codes) {
  const codeParts = code.split(/\s+/);
  const searchPattern = codeParts.join("\\s*");
  const regex = new RegExp(searchPattern.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "i");
  
  const matches = allFiles.filter(f => regex.test(f.name));
  console.log("[" + code + "] 找到 " + matches.length + " 个匹配:");
  for (const m of matches.slice(0, 5)) {
    const folder = require("path").basename(require("path").dirname(m.fullPath));
    console.log("  [" + folder + "] " + m.name);
  }
  if (matches.length > 5) console.log("  ... 还有 " + (matches.length - 5) + " 个");
  console.log("");
}
