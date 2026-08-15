const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const root = "D:\\电子规范";
const data = JSON.parse(fs.readFileSync("D:/_all_files.json", "utf8"));

// === Categorize each file ===
function getStandardCode(name) {
  const upper = name.toUpperCase();
  const codes = [];
  const gb = upper.match(/(?:GB|GB\/T|GBJ)\s*5?\d{2,5}(?:-\d{4})?/);
  if (gb) codes.push("国标");
  const jt = upper.match(/(?:JTJ|JTG|JTG\/T|JT\/T)\s*[A-Z]?\s*\d{1,4}(?:-\d{4})?/);
  if (jt) codes.push("交通部");
  const js = upper.match(/(?:CJJ|CJ\/T|JGJ|JGJ\/T)\s*\d{1,4}(?:-\d{4})?/);
  if (js) codes.push("建设部");
  const sl = upper.match(/(?:SL|SL\/T|DL|DL\/T|NB)\s*\d{1,4}(?:-\d{4})?/);
  if (sl) codes.push("水工");
  const db = upper.match(/(?:DB\d{2}\/\d{1,4}|DBJ\s*\d{1,2}|DGJ\s*\d{1,2})/);
  if (db) codes.push("地方");
  const forCode = upper.match(/(?:AASHTO|ASTM|BS\s*\d|EN\s*\d|ISO\s*\d|DIN|ACI|EUROCODE|FIDIC)/);
  if (forCode) codes.push("国外");
  return codes;
}

function categorizeFile(name, fullPath) {
  const upper = name.toUpperCase();
  const folderName = path.basename(path.dirname(fullPath));
  
  const codes = getStandardCode(name);
  if (codes.length > 0) {
    const t = codes[0];
    if (t === "国标") return "01-国标规范(GB)";
    if (t === "交通部") return "02-交通部规范(JTJ_JTG)";
    if (t === "建设部") return "03-建设部规范(CJJ_JGJ)";
    if (t === "水工") return "06-水工规范(SL_DL)";
    if (t === "地方") return "04-地方规范及指引(DB)";
    if (t === "国外") return "05-国外规范";
  }
  
  // folder-based fallback
  if (folderName.includes("17-国外规范") || folderName.includes("国外规范")) return "05-国外规范";
  if (folderName.includes("16-铝合金") || folderName.includes("铝合金")) return "07-其他规范\\铝合金结构";
  if (folderName.includes("19-注册考试") || folderName.includes("注册考试")) return "07-其他规范\\注册考试资料";
  if (folderName.includes("09-材料") || folderName.includes("材料标准")) return "07-其他规范\\材料标准";
  if (folderName.includes("10-施工") || folderName.includes("施工验收")) return "07-其他规范\\施工验收";
  if (folderName.includes("15-绿化") || folderName.includes("绿化环保")) return "07-其他规范\\绿化环保";
  if (folderName.includes("11-造价") || folderName.includes("概预算")) return "07-其他规范\\造价概预算";
  if (folderName.includes("14-焊接") || folderName.includes("焊接规范")) return "07-其他规范\\焊接规范";
  if (folderName.includes("18-法规") || folderName.includes("法规法律")) return "07-其他规范\\法规法律";
  if (folderName.includes("20-其他") || folderName.includes("其他")) return "07-其他规范\\未分类";
  
  // keyword-based fallback
  if (/上海市|浙江省|江苏省|广东省|北京市|天津市|重庆市|福建|湖北|湖南|山东|四川|安徽|河北|山西|辽宁|吉林|黑龙江|江西|河南|海南|贵州|云南|陕西|甘肃|青海|广西|内蒙古|西藏|宁夏|新疆|深圳|广州|杭州|成都/.test(name)) return "04-地方规范及指引(DB)";
  if (/地方标准|地方规范|省标/.test(name)) return "04-地方规范及指引(DB)";
  if (/水利|水电|水工|水力|河道|防洪|灌溉|水库|水文|水资源/.test(name)) return "06-水工规范(SL_DL)";
  if (/公路|桥梁|桥涵|隧道|路面|路基|交通工程|客运|货运|港口|航道|水运|码头|道路|高速公路|立交/.test(name)) return "02-交通部规范(JTJ_JTG)";
  if (/建筑|城镇|城市|住宅|房地产|工程勘察|地基基础|结构设计|混凝土|抗震|防火|给水|排水|暖通|电气|智能/.test(name)) return "03-建设部规范(CJJ_JGJ)";
  
  return "07-其他规范\\未分类";
}

// === Create directories and move files ===
const dirs = new Set();
const moveMap = {};

for (const f of data) {
  const cat = categorizeFile(f.name, f.fullPath);
  if (!moveMap[cat]) moveMap[cat] = [];
  moveMap[cat].push(f);
  dirs.add(cat);
}

// Create temp directories list
const sortedDirs = [...dirs].sort();
console.log("=== 创建目录结构 ===\n");
for (const d of sortedDirs) {
  const target = path.join(root, d);
  fs.mkdirSync(target, { recursive: true });
  console.log("  ✓ 创建: " + d);
}

console.log("\n=== 开始移动文件 ===\n");
let moved = 0;
let failed = 0;
let totalSize = 0;

for (const [cat, files] of Object.entries(moveMap)) {
  console.log("--- " + cat + " (" + files.length + " 个文件) ---");
  for (const f of files) {
    const targetDir = path.join(root, cat);
    const targetPath = path.join(targetDir, f.name);
    try {
      fs.renameSync(f.fullPath, targetPath);
      moved++;
      totalSize += f.size;
    } catch (e) {
      // If file already exists at target, add a suffix
      if (e.code === "EEXIST" || (e.message && e.message.includes("exists"))) {
        const ext = path.extname(f.name);
        const base = path.basename(f.name, ext);
        let newName = base + "_moved" + ext;
        let counter = 1;
        while (fs.existsSync(path.join(targetDir, newName))) {
          counter++;
          newName = base + "_moved" + counter + ext;
        }
        try {
          fs.renameSync(f.fullPath, path.join(targetDir, newName));
          moved++;
          totalSize += f.size;
          console.log("  ⚠ 重名: " + f.name + " -> " + newName);
        } catch (e2) {
          failed++;
          console.log("  ✗ 失败: " + f.name + " - " + e2.message);
        }
      } else {
        failed++;
        console.log("  ✗ 失败: " + f.name + " - " + e.message);
      }
    }
  }
}

console.log("\n=== 完成 ===");
console.log("成功移动: " + moved + " 个文件");
console.log("失败: " + failed + " 个文件");
console.log("移动总大小: " + (totalSize / 1024 / 1024 / 1024).toFixed(2) + " GB");

// Output summary per category
console.log("\n=== 各分类移动汇总 ===\n");
const sortedEntries = Object.entries(moveMap).sort((a, b) => b[1].length - a[1].length);
for (const [cat, files] of sortedEntries) {
  const sizeMB = files.reduce((s, f) => s + f.size, 0) / 1024 / 1024;
  console.log("  " + cat + ": " + files.length + " 个文件, " + sizeMB.toFixed(1) + " MB");
}
