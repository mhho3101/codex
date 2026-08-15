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

function isCodeOnly(name) {
  const ext = path.extname(name);
  const base = path.basename(name, ext);
  const hasChinese = /[\u4e00-\u9fff]/.test(base);
  const codePattern = /^(?:GB|GB\/T|GBJ|JTJ|JTG|CJJ|CJ\/T|JGJ|SL|DL|NB|DB\d{2}\/|DBJ|DGJ|AASHTO|ASTM|BS|EN|ISO|DIN|ACI|ASCE|IBC|NFPA|FIDIC|AS\s*\d|NZS|JTG\/T)\s*[A-Z\/]?\s*\d{1,5}(?:-\d{4})?$/i;
  return !hasChinese && codePattern.test(base.trim());
}

// Also find files that have the code as a SUFFIX in parens (standard format)
function extractNameFromMatch(matchName, code) {
  const ext = path.extname(matchName);
  const base = path.basename(matchName, ext);
  // Remove the code and surrounding parens
  const codeEscaped = code.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  // Remove " (code)" or "(code)" from the end
  let cleaned = base.replace(new RegExp("\\s*\\(\\s*" + codeEscaped + "\\s*\\)\\s*$", "i"), "");
  // Remove any remaining 《》 
  cleaned = cleaned.replace(/[《》]/g, "").trim();
  // Remove empty parens
  cleaned = cleaned.replace(/\(\s*\)/g, "").trim();
  return cleaned;
}

const codeOnlyFiles = allFiles.filter(f => isCodeOnly(f.name));

// Build a map: code -> [files with that code in their name]
const codeToFiles = {};
for (const f of allFiles) {
  const ext = path.extname(f.name);
  const base = path.basename(f.name, ext);
  // Extract any code from the filename
  const codeMatch = base.match(/((?:GB|GB\/T|GBJ|JTJ|JTG|CJJ|CJ\/T|JGJ|SL|DL|NB|DB\d{2}\/|DBJ|DGJ|AASHTO|ASTM|BS|EN|ISO|DIN|ACI|ASCE|IBC|NFPA|FIDIC|AS\s*\d|NZS|JTG\/T)\s*[A-Z\/]?\s*\d{1,5}(?:-\d{4})?)/i);
  if (codeMatch && /[\u4e00-\u9fff]/.test(base)) {
    const code = codeMatch[1].trim().replace(/\s+/g, " ");
    if (!codeToFiles[code]) codeToFiles[code] = [];
    codeToFiles[code].push(f);
  }
}

let renamed = 0;
let unmatched = [];

for (const codeFile of codeOnlyFiles) {
  const ext = path.extname(codeFile.name);
  const base = path.basename(codeFile.name, ext).trim();
  const code = base;
  
  if (codeToFiles[code] && codeToFiles[code].length > 0) {
    const match = codeToFiles[code][0];
    const chineseName = extractNameFromMatch(match.name, code);
    
    if (chineseName) {
      const newName = chineseName + " (" + code + ")" + ext;
      const newPath = path.join(codeFile.dir, newName);
      
      try {
        fs.renameSync(codeFile.fullPath, newPath);
        renamed++;
        console.log("  ✓ " + codeFile.name + "  ->  " + newName + "  [来源: " + match.name + "]");
      } catch (e) {
        console.log("  ✗ " + codeFile.name + "  -> 失败: " + e.message);
      }
    } else {
      unmatched.push(codeFile);
    }
  } else {
    unmatched.push(codeFile);
  }
}

console.log("\n已完成: " + renamed + " 个");
if (unmatched.length > 0) {
  console.log("\n无法匹配的文件 (" + unmatched.length + " 个):");
  for (const f of unmatched) {
    const folder = path.basename(f.dir);
    console.log("  [" + folder + "] " + f.name);
  }
}
