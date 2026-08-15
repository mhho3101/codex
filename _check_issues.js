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

// Find files with issues
let issues = 0;
for (const f of allFiles) {
  const base = path.basename(f.name, path.extname(f.name));
  const issues_list = [];
  if (/\(\(/.test(base)) issues_list.push("双括号");
  if (/\(\)/.test(base)) issues_list.push("空括号");
  if (/\(\)/.test(base)) issues_list.push("空括号");
  if (/^\s*\(/.test(base)) issues_list.push("开头括号");
  if (base.includes("((")) issues_list.push("双开括号");
  if (base.endsWith("(") || base.endsWith(")（") || base.endsWith("）")) issues_list.push("结尾括号");
  if (/\*/.test(base)) issues_list.push("含星号");
  if (/\s\(\s/.test(base)) issues_list.push("括号前空格");
  if (issues_list.length > 0) {
    issues++;
    if (issues <= 30) {
      console.log(f.name + "  [" + issues_list.join(", ") + "]");
    }
  }
}

console.log("\n存在问题文件数: " + issues);
