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
    else if (entry.isFile()) {
      const folder = path.basename(dir);
      allFiles.push({ fullPath: full, name: entry.name, folder });
    }
  }
}
walk(root);

// Search for partial matches of the codes
const codes = [
  { code: "GB 50289-2016", num: "50289" },
  { code: "GB 50688-2011", num: "50688" },
  { code: "GB 50763-2012", num: "50763" },
  { code: "JTG 3450-2019", num: "3450" },
  { code: "JTG B 05-2015", num: "B05" },
  { code: "JTG D 30-2015", num: "D30" },
  { code: "JTG D 61-2005", num: "D61" },
  { code: "JTG D 63-2007", num: "D63" },
  { code: "JTG E 30-2005", num: "E30" },
  { code: "JTG E 60-2008", num: "E60" },
  { code: "CJJ 11-2011", num: "CJJ11" },
  { code: "CJJ 194-2013", num: "CJJ194" },
  { code: "CJJ 221-2015", num: "CJJ221" },
  { code: "CJJ 56-2012", num: "CJJ56" },
  { code: "CJJ 69-1995", num: "CJJ69" },
  { code: "AS 1743-2001", num: "1743" },
  { code: "AS 1744-1975", num: "1744" },
];

for (const { code, num } of codes) {
  const regex = new RegExp(num.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "i");
  const matches = allFiles.filter(f => regex.test(f.name));
  console.log("[" + code + "] (" + num + "):");
  if (matches.length > 0) {
    for (const m of matches.slice(0, 3)) {
      console.log("  [" + m.folder + "] " + m.name);
    }
  } else {
    console.log("  (无匹配)");
  }
  console.log("");
}
