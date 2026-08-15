const fs = require("fs");
const path = require("path");

const data = JSON.parse(fs.readFileSync("D:/_all_files.json", "utf8"));

// Comprehensive categorization - first pass: extract standard code
// Then fallback: use folder name
function getStandardCode(name) {
  const upper = name.toUpperCase();
  // Try to find standard codes
  const codes = [];
  // GB
  const gb = upper.match(/(?:GB|GB\/T|GBJ)\s*5?\d{2,5}(?:-\d{4})?/);
  if (gb) codes.push({ code: gb[0], type: "国标" });
  // JTJ/JTG
  const jt = upper.match(/(?:JTJ|JTG|JTG\/T|JT\/T)\s*[A-Z]?\s*\d{1,4}(?:-\d{4})?/);
  if (jt) codes.push({ code: jt[0], type: "交通部" });
  // CJJ/JGJ
  const js = upper.match(/(?:CJJ|CJ\/T|JGJ|JGJ\/T)\s*\d{1,4}(?:-\d{4})?/);
  if (js) codes.push({ code: js[0], type: "建设部" });
  // SL/DL/NB
  const sl = upper.match(/(?:SL|SL\/T|DL|DL\/T|NB)\s*\d{1,4}(?:-\d{4})?/);
  if (sl) codes.push({ code: sl[0], type: "水工" });
  // DB
  const db = upper.match(/(?:DB\d{2}\/\d{1,4}|DBJ\s*\d{1,2}|DGJ\s*\d{1,2})/);
  if (db) codes.push({ code: db[0], type: "地方" });
  // Foreign
  const forCode = upper.match(/(?:AASHTO|ASTM|BS\s*\d|EN\s*\d|ISO\s*\d|DIN|ACI|EUROCODE|FIDIC)/);
  if (forCode) codes.push({ code: forCode[0], type: "国外" });
  return codes;
}

function categorizeByFolder(folderName) {
  const f = folderName;
  if (f.includes("01-") || f.includes("公路")) return "交通部规范(JTJ/JTG)";
  if (f.includes("02-") || f.includes("桥梁")) return "交通部规范(JTJ/JTG)";
  if (f.includes("03-") || f.includes("市政")) return "建设部规范(CJJ/JGJ)";
  if (f.includes("04-") || f.includes("建筑")) return "建设部规范(CJJ/JGJ)";
  if (f.includes("05-") || f.includes("隧道")) return "交通部规范(JTJ/JTG)";
  if (f.includes("06-") || f.includes("水运")) return "水工规范(SL/DL)";
  if (f.includes("07-") || f.includes("水利") || f.includes("水电")) return "水工规范(SL/DL)";
  if (f.includes("08-") || f.includes("地质") || f.includes("岩土")) return "建设部规范(CJJ/JGJ)";
  if (f.includes("09-") || f.includes("材料")) return "其他-材料标准";
  if (f.includes("10-") || f.includes("施工")) return "其他-施工验收";
  if (f.includes("11-") || f.includes("造价")) return "其他-造价概预算";
  if (f.includes("12-") || f.includes("抗震")) return "建设部规范(CJJ/JGJ)";
  if (f.includes("13-") || f.includes("交通") || f.includes("安全设施")) return "交通部规范(JTJ/JTG)";
  if (f.includes("14-") || f.includes("焊接")) return "其他-焊接规范";
  if (f.includes("15-") || f.includes("绿化") || f.includes("环保")) return "其他-绿化环保";
  if (f.includes("16-") || f.includes("铝合金")) return "其他-铝合金结构";
  if (f.includes("17-") || f.includes("国外规范")) return "国外规范";
  if (f.includes("18-") || f.includes("法规")) return "其他-法规法律";
  if (f.includes("19-") || f.includes("注册考试")) return "其他-注册考试资料";
  if (f.includes("20-") || f.includes("其他")) return "20-其他";
  return "其他规范";
}

const cats = {};
for (const f of data) {
  const folderName = path.basename(path.dirname(f.fullPath));
  const codes = getStandardCode(f.name);
  let cat;
  if (codes.length > 0) {
    // Use the most specific code type
    const type = codes[0].type;
    if (type === "国标") cat = "国标规范(GB)";
    else if (type === "交通部") cat = "交通部规范(JTJ/JTG)";
    else if (type === "建设部") cat = "建设部规范(CJJ/JGJ)";
    else if (type === "水工") cat = "水工规范(SL/DL)";
    else if (type === "地方") cat = "地方规范及指引(DB)";
    else if (type === "国外") cat = "国外规范";
    else cat = "其他规范";
  } else {
    // Fallback to folder-based categorization
    cat = categorizeByFolder(folderName);
  }
  if (!cats[cat]) cats[cat] = [];
  cats[cat].push(f);
}

const sorted = Object.entries(cats).sort((a, b) => b[1].length - a[1].length);
console.log("=== 最终分类结果 (按标准类型) ===\n");
for (const [cat, files] of sorted) {
  const sizeMB = files.reduce((s, f) => s + f.size, 0) / 1024 / 1024;
  console.log("  " + cat + ": " + files.length + " 个文件, " + sizeMB.toFixed(1) + " MB");
}

// Output detailed file list per category
console.log("\n\n=== 详细文件清单 ===\n");
for (const [cat, files] of sorted) {
  console.log("--- " + cat + " ---");
  for (const f of files) {
    const folder = path.basename(path.dirname(f.fullPath));
    console.log("  [" + folder + "] " + f.name + "  " + Math.round(f.size/1024) + "KB");
  }
  console.log("");
}
