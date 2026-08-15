const fs = require("fs");
const crypto = require("crypto");
const path = require("path");

const data = JSON.parse(fs.readFileSync("D:/_all_files.json", "utf8"));

const sizeGroups = {};
for (const f of data) {
  if (!sizeGroups[f.size]) sizeGroups[f.size] = [];
  sizeGroups[f.size].push(f);
}

const sameSizeGroups = Object.entries(sizeGroups).filter(([, g]) => g.length > 1).sort((a, b) => b[1].length - a[1].length);

console.log("同大小文件组数: " + sameSizeGroups.length);
console.log("涉及文件数: " + sameSizeGroups.reduce((s, [, g]) => s + g.length, 0) + "\n");

let totalDup = 0;
let totalDupMB = 0;
const dupRecords = [];

for (const [size, files] of sameSizeGroups) {
  const withHash = files.map(f => {
    try {
      const fd = fs.openSync(f.fullPath, "r");
      const stat = fs.fstatSync(fd);
      const chunk = 64 * 1024 * 1024;
      const hash = crypto.createHash("sha256");
      let pos = 0;
      const buf = Buffer.alloc(Math.min(chunk, stat.size));
      while (pos < stat.size) {
        const bytes = fs.readSync(fd, buf, 0, Math.min(chunk, stat.size - pos), pos);
        if (bytes <= 0) break;
        hash.update(buf.slice(0, bytes));
        pos += bytes;
      }
      fs.closeSync(fd);
      return { ...f, hash: hash.digest("hex") };
    } catch (e) {
      return { ...f, hash: "ERR:" + e.message };
    }
  });
  
  const hashGroups = {};
  for (const f of withHash) {
    if (!hashGroups[f.hash]) hashGroups[f.hash] = [];
    hashGroups[f.hash].push(f);
  }
  
  const realDupes = Object.entries(hashGroups).filter(([, g]) => g.length > 1 && !g[0].hash.startsWith("ERR"));
  for (const [h, flist] of realDupes) {
    const keep = flist[0];
    const redundant = flist.slice(1);
    const sizeMB = redundant.reduce((s, f) => s + f.size, 0) / 1024 / 1024;
    totalDup += redundant.length;
    totalDupMB += sizeMB;
    dupRecords.push({ keep, redundant, sizeMB });
    console.log("[" + flist.length + "x] " + size + " bytes | " + keep.name + "  (冗余 " + sizeMB.toFixed(1) + " MB)");
    for (const f of flist) {
      const folder = path.basename(path.dirname(f.fullPath));
      console.log("  " + (f === keep ? "> 保留: " : "  删除: ") + "[" + folder + "] " + f.name);
    }
    console.log("");
  }
}

console.log("=== 总结 ===");
console.log("全网内容重复文件组数: " + dupRecords.length);
console.log("可删除冗余文件数: " + totalDup);
console.log("可释放空间: " + totalDupMB.toFixed(1) + " MB");
