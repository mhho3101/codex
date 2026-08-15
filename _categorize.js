const fs = require("fs");
const path = require("path");

const data = JSON.parse(fs.readFileSync("D:/_all_files.json", "utf8"));

// Enhanced categorization
function categorize(name, folder) {
  const upper = name.toUpperCase();
  const folderName = path.basename(folder);
  
  // 注册考试资料 - 单独处理
  if (folderName.includes("注册考试") || folderName.includes("19-")) return "19-注册考试资料";
  // 法规法律
  if (folderName.includes("法规法律") || folderName.includes("18-")) return "18-法规法律";
  // 国外规范 folder
  if (folderName.includes("国外规范") || folderName.includes("17-")) return "国外规范";
  // 造价概预算
  if (folderName.includes("造价") || folderName.includes("11-")) return "其他-造价概预算";
  // 绿化环保
  if (folderName.includes("绿化") || folderName.includes("15-")) return "其他-绿化环保";
  // 焊接规范
  if (folderName.includes("焊接") || folderName.includes("14-")) return "其他-焊接规范";
  // 注册考试资料
  if (folderName.includes("注册考试") || folderName.includes("19-")) return "19-注册考试资料";
  // 其他
  if (folderName.includes("其他") || folderName.includes("20-")) return "20-其他";
  
  // 国标 (GB开头或在文件名中)
  if (/^GB\b/.test(upper) || /^GB\//.test(upper) || /^GBJ\b/.test(upper) || /^GB5\d{2}/.test(upper)) return "国标规范(GB)";
  if (/\bGB\s*\d/.test(upper) || /\bGB\/T\b/.test(upper)) return "国标规范(GB)";
  
  // 交通部 (JTJ/JTG/JT)
  if (/^JTJ\b/.test(upper) || /^JTG\b/.test(upper) || /^JT\//.test(upper) || /^JTG\//.test(upper)) return "交通部规范(JTJ/JTG)";
  if (/\bJTJ\s*\d/.test(upper) || /\bJTG\s*\d/.test(upper) || /\bJT\/T\b/.test(upper)) return "交通部规范(JTJ/JTG)";
  
  // 建设部 (CJJ/JGJ)
  if (/^CJJ\b/.test(upper) || /^CJ\b/.test(upper) || /^JGJ\b/.test(upper) || /^JG\b/.test(upper)) return "建设部规范(CJJ/JGJ)";
  if (/\bCJJ\s*\d/.test(upper) || /\bJGJ\s*\d/.test(upper)) return "建设部规范(CJJ/JGJ)";
  
  // 水工 (SL/DL/NB)
  if (/^SL\b/.test(upper) || /^SL\//.test(upper) || /^DL\b/.test(upper) || /^DL\//.test(upper) || /^NB\b/.test(upper)) return "水工规范(SL/DL)";
  if (/\bSL\s*\d/.test(upper) || /\bDL\s*\d/.test(upper) || /\bNB\s*\d/.test(upper)) return "水工规范(SL/DL)";
  
  // 地方 (DB)
  if (/^DB\d+/.test(upper) || /^DBJ\b/.test(upper) || /^DGJ\b/.test(upper)) return "地方规范及指引(DB)";
  if (/\bDB\d{2}\//.test(upper)) return "地方规范及指引(DB)";
  
  // 国外 (AASHTO, ASTM, BS, EN, ISO, DIN, ACI, ASCE, IBC, NFPA, EUROCODE)
  if (/^AASHTO/.test(upper) || /^ASTM\b/.test(upper) || /^BS\s*\d/.test(upper) || /^EN\s*\d/.test(upper) || 
      /^ISO\b/.test(upper) || /^DIN\b/.test(upper) || /^ACI\b/.test(upper) || /^ASCE\b/.test(upper) || 
      /^IBC\b/.test(upper) || /^NFPA\b/.test(upper)) return "国外规范";
  if (/\bAASHTO\b/.test(upper) || /\bASTM\b/.test(upper) || /\bEUROCODE\b/.test(upper) || /\bFIDIC\b/.test(upper)) return "国外规范";
  
  // 地方 keywords
  if (/上海市|浙江省|江苏省|广东省|北京市|天津市|重庆市|福建|湖北|湖南|山东|四川|安徽|河北|山西|辽宁|吉林|黑龙江|江西|河南|海南|贵州|云南|陕西|甘肃|青海|广西|内蒙古|西藏|宁夏|新疆|深圳|广州|杭州|成都/.test(name)) return "地方规范及指引(DB)";
  if (/地方标准|地方规范|省标|地标/.test(name)) return "地方规范及指引(DB)";
  
  // 水工 keywords
  if (/水利|水电|水工|水力|河道|防洪|灌溉|水库|水文|水资源/.test(name)) return "水工规范(SL/DL)";
  
  // 交通部 keywords
  if (/公路|桥梁|桥涵|隧道|路面|路基|交通工程|客运|货运|港口|航道|水运|码头|道路|高速公路|立交/.test(name)) return "交通部规范(JTJ/JTG)";
  
  // 建设部 keywords
  if (/建筑|城镇|城市|住宅|房地产|工程勘察|地基基础|结构设计|混凝土|抗震|防火|给水|排水|暖通|电气|智能/.test(name)) return "建设部规范(CJJ/JGJ)";
  
  // 国标 keywords
  if (/国标|国家标准|GB\s*\d/.test(name)) return "国标规范(GB)";
  
  // 铝合金结构
  if (folderName.includes("铝合金") || folderName.includes("16-")) return "其他-铝合金结构";
  
  return "其他规范";
}

const cats = {};
const fileMap = {};
for (const f of data) {
  const folder = f.fullPath;
  const cat = categorize(f.name, folder);
  if (!cats[cat]) cats[cat] = [];
  cats[cat].push(f);
}

const sorted = Object.entries(cats).sort((a, b) => b[1].length - a[1].length);
console.log("规范类型分类结果:\n");
for (const [cat, files] of sorted) {
  const sizeMB = files.reduce((s, f) => s + f.size, 0) / 1024 / 1024;
  console.log("  " + cat + ": " + files.length + " 个文件, " + sizeMB.toFixed(1) + " MB");
}

console.log("\n=== 重新分类后 \"其他规范\" 细分 ===");
const others = cats["其他规范"] || [];
if (others.length > 0) {
  const subCats = {};
  for (const f of others) {
    const folder = path.basename(path.dirname(f.fullPath));
    if (!subCats[folder]) subCats[folder] = [];
    subCats[folder].push(f);
  }
  const subSorted = Object.entries(subCats).sort((a, b) => b[1].length - a[1].length);
  for (const [sub, files] of subSorted) {
    const sizeMB = files.reduce((s, f) => s + f.size, 0) / 1024 / 1024;
    console.log("  " + sub + ": " + files.length + " 个文件, " + sizeMB.toFixed(1) + " MB");
  }
}
