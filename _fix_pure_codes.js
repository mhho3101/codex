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

// Find files that are JUST a code (no Chinese name)
function isCodeOnly(name) {
  const ext = path.extname(name);
  const base = path.basename(name, ext);
  // Check if the base is just a standard code pattern with no Chinese characters
  const hasChinese = /[\u4e00-\u9fff]/.test(base);
  const codePattern = /^(?:GB|GB\/T|GBJ|JTJ|JTG|CJJ|CJ\/T|JGJ|SL|DL|NB|DB\d{2}\/|DBJ|DGJ|AASHTO|ASTM|BS|EN|ISO|DIN|ACI|ASCE|IBC|NFPA|FIDIC|AS\s*\d|NZS|JTG\/T)\s*[A-Z\/]?\s*\d{1,5}(?:-\d{4})?$/i;
  return !hasChinese && codePattern.test(base.trim());
}

const codeOnlyFiles = [];
for (const f of allFiles) {
  if (isCodeOnly(f.name)) {
    codeOnlyFiles.push(f);
  }
}

console.log("仅含版本号的文件数: " + codeOnlyFiles.length + "\n");

// For each code-only file, find matching files with full names
// Group by folder first
const codeOnlyByFolder = {};
for (const f of codeOnlyFiles) {
  const folder = f.dir;
  if (!codeOnlyByFolder[folder]) codeOnlyByFolder[folder] = [];
  codeOnlyByFolder[folder].push(f);
}

// Now for each folder, find the full-name files
const renameMap = {};
for (const [folder, files] of Object.entries(codeOnlyByFolder)) {
  // Get all files in this folder
  const folderFiles = allFiles.filter(f => f.dir === folder);
  
  for (const codeFile of files) {
    const ext = path.extname(codeFile.name);
    const base = path.basename(codeFile.name, ext).trim();
    
    // Try to find a matching file with the same code and a Chinese name
    // Look for files that contain the code in the name (not just the code itself)
    const codeEscaped = base.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const matching = folderFiles.filter(f => {
      if (f.fullPath === codeFile.fullPath) return false;
      const hasChinese = /[\u4e00-\u9fff]/.test(f.name);
      return hasChinese && new RegExp(codeEscaped, "i").test(f.name);
    });
    
    if (matching.length > 0) {
      // Use the name from the matching file
      const matchName = matching[0].name;
      const matchExt = path.extname(matchName);
      const matchBase = path.basename(matchName, matchExt);
      
      // Extract the Chinese name part (before the code)
      let chineseName = matchBase.replace(new RegExp(codeEscaped, "i"), "").trim();
      chineseName = chineseName.replace(/[《》]/g, "").trim();
      chineseName = chineseName.replace(/[\(\（][^\)\）]*$/, "").trim();
      chineseName = chineseName.replace(/\s+$/, "");
      
      if (chineseName) {
        renameMap[codeFile.fullPath] = {
          oldName: codeFile.name,
          newName: chineseName + " (" + base + ")" + ext,
          sourceFile: matchName
        };
      }
    }
  }
}

console.log("可匹配补全的文件: " + Object.keys(renameMap).length + "\n");
for (const [oldPath, info] of Object.entries(renameMap)) {
  console.log("  " + info.oldName + "  ->  " + info.newName + "  [参考: " + info.sourceFile + "]");
}

// Also show unmatched files
const unmatched = codeOnlyFiles.filter(f => !renameMap[f.fullPath]);
if (unmatched.length > 0) {
  console.log("\n无法匹配的文件 (" + unmatched.length + " 个):");
  for (const f of unmatched) {
    const folder = path.basename(f.dir);
    console.log("  [" + folder + "] " + f.name);
  }
}
