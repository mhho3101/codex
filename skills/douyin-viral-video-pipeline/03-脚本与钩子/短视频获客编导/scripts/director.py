#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
content-director 引擎（零依赖 · 纯标准库 · 离线可跑）

子命令:
  onboard <id> <名称> <行业> <CTA>   建客户七件套 + matrix 词表模板
  status                             所有客户的编导作战台（缺口/进度/下一步）
  state <cid>                        查看客户运行状态（六态/回炉/挂起/轨迹）（v2 新增）
  state <cid> set --state X --step Y --event Z   更新运行状态（v2 新增）
  predict <cid> <slug>               写盲预测（发布前；写完不可改）（v3 新增）
  shoot <cid> <slug>                 登记已拍未发，buffer +1（v3 新增）
  publish <cid> <slug>               登记已发布，buffer -1（v3 新增）
  retro <cid> <slug>                 追加复盘段（只追加不改预测）（v3 新增）
  recommend <cid>                    buffer 感知推荐下一批（1稳+1实验）（v3 新增）
  bump <cid>                         标准卡升级工作表（全量重打校验）（v3 新增）
  persona <cid>                      回标评论聚类出受众画像骨架（v3 新增）
  check <file> [--client <cid>]    文案三关校验+合规扫描：支持读客户标准卡机判校准（v3.4）
  aha <cid>                          Aha 判级：自动算近10条基准线，标超基线条目（v3.3 新增）
  patrol                             每日巡检：挂起超期/buffer红灯/待复盘/待回标一扫全客户（v3.3 新增）
  schedule <cid>                     排期纪律机判：钩子限频+信任类占比（v3.3 新增）
  seed <cid>                         冷启动搜索任务清单生成（v3.3 新增）
  archive <cid>                      客户归档到 clients/_archive（v3.3 新增）
  migrate [cid]                      老客户目录补齐 v2/v3 新文件并打 schema 标（v3 新增）
  matrix <cid> [--llm]               连连看需求组合出题池（行业核心×行业相关×人群场景）
  assemble <cid>                     钩子库 23 类 × 客户痛点 装配「推荐页」候选
  score                              交互式过 8 项评分闸门（S/A/B 判定）
  metrics                            钩子覆盖率/回标率/钩子用量分布

客户数据存当前目录 clients/（用户私有，勿提交公开仓库）。
--llm 增强读环境变量: TOPIC_LLM_BASE_URL / TOPIC_LLM_API_KEY / TOPIC_LLM_MODEL（缺失自动回退）。
"""
import re, os, csv, json, sys, itertools, datetime

BASE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.normpath(os.path.join(BASE, "..", "references", "hook-library.md"))
CLIENTS = os.path.join(os.getcwd(), "clients")

FIVE = [("00-console.md", "客户总控台"), ("01-topics.md", "选题库"), ("02-scripts.md", "脚本库"),
        ("03-benchmarks.md", "对标库"), ("04-learning.md", "学习与复盘日志")]


def reg_path():
    return os.path.join(CLIENTS, "registry.json")


def load_registry():
    if os.path.exists(reg_path()):
        return json.load(open(reg_path(), encoding="utf-8"))
    return {}


def save_registry(r):
    os.makedirs(CLIENTS, exist_ok=True)
    json.dump(r, open(reg_path(), "w", encoding="utf-8"), ensure_ascii=False, indent=2)


# ---------------- onboard ----------------

TPL = os.path.join(BASE, "..", "templates")

def cmd_onboard(cid, name, industry, cta):
    reg = load_registry()
    if cid in reg:
        print(f"{cid} 已存在（{reg[cid]['name']}），跳过建库。")
    else:
        reg[cid] = {"name": name, "industry": industry, "cta": cta,
                    "created": datetime.date.today().isoformat()}
        save_registry(reg)
    cdir = os.path.join(CLIENTS, cid)
    os.makedirs(cdir, exist_ok=True)
    mapping = {"00-console.md": "client-console.md", "01-topics.md": "topic-library.md",
               "02-scripts.md": "script-library.md", "03-benchmarks.md": "benchmark-library.md",
               "04-learning.md": "learning-log.md", "05-state.md": "running-state.md",
               "06-standard.md": "standard-card.md"}
    for target, tpl in mapping.items():
        tp = os.path.join(cdir, target)
        if not os.path.exists(tp):
            src = os.path.join(TPL, tpl)
            body = open(src, encoding="utf-8").read() if os.path.exists(src) else f"# {target}\n"
            body = body.replace("{{CLIENT_ID}}", cid).replace("{{CLIENT_NAME}}", name)\
                       .replace("{{INDUSTRY}}", industry).replace("{{CTA}}", cta)\
                       .replace("{{DATE}}", datetime.date.today().isoformat())
            open(tp, "w", encoding="utf-8").write(body)
    mj = os.path.join(cdir, "matrix.json")
    if not os.path.exists(mj):
        json.dump({"core": "填行业核心词(1个)",
                   "related": ["填行业相关词8-12个：只能来自采访原话/评论区/搜索联想"],
                   "personas": ["填人群/场景10-15个：角色+处境"]},
                  open(mj, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"✅ 客户 {cid}（{name}）已建在 clients/{cid}/：五件套 + 运行状态 + 标准卡 + matrix.json 词表模板")
    print(f"下一步：① 按 references/planning.md 完成采访与定位五步，填 00-console.md 并合成定位卡")
    print(f"       ② 填 clients/{cid}/matrix.json 词表（不编造客户事实）")
    print(f"       ③ python director.py matrix {cid}")


# ---------------- status（作战台） ----------------

def cmd_status():
    reg = load_registry()
    if not reg:
        print("还没有任何客户。先跑：python director.py onboard <id> <名称> <行业> <CTA>")
        return
    print("== 编导作战台 ==")
    rows = []
    for cid, c in reg.items():
        if c.get("archived"):
            continue
        cdir = os.path.join(CLIENTS, cid)
        state_txt, buf, hang = None, 0, ""
        sp = os.path.join(cdir, STATE_FILE)
        if os.path.exists(sp):
            body = open(sp, encoding="utf-8").read()
            m = re.search(r"^- 状态机：(.+)$", body, re.M)
            state_txt = m.group(1).strip() if m else None
            buf = get_buffer(body)
            hm = re.search(r"^- 等什么：(.+)$", body, re.M)
            hang = (hm.group(1).strip() if hm else "") or ""
        console = os.path.join(cdir, "00-console.md")
        positioned = os.path.exists(console) and "[未定位]" not in open(console, encoding="utf-8").read()
        topics = os.path.join(cdir, "01-topics.md")
        n_topics = len([h for h in re.findall(r'^###\s.*', open(topics, encoding="utf-8").read(), re.M)
                        if "[" not in h]) if os.path.exists(topics) else 0
        scripts = os.path.join(cdir, "02-scripts.md")
        s_text = open(scripts, encoding="utf-8").read() if os.path.exists(scripts) else ""
        n_scripts = len([h for h in re.findall(r'^###\s.*', s_text, re.M) if "[" not in h])
        n_tagged = len(re.findall(r'实际数据：[^\n]*\d', s_text))
        gap = "定位" if not positioned else ("选题" if n_topics < 10 else
              ("稿子" if n_scripts == 0 else ("数据回标" if n_tagged < n_scripts else "复利沉淀")))
        nxt = {"定位": "模块A 策划诊断", "选题": "模块B 选题生成", "稿子": "模块C 脚本生产",
               "数据回标": "模块E 数据回标", "复利沉淀": "模块F 复利沉淀"}[gap]
        rows.append({"cid": cid, "c": c, "state": state_txt, "buf": buf, "hang": hang,
                     "positioned": positioned, "n_topics": n_topics, "n_scripts": n_scripts,
                     "n_tagged": n_tagged, "gap": gap, "nxt": nxt})
    rows.sort(key=lambda r: (-r["buf"], 0 if r["hang"] else 1, r["cid"]))
    for r in rows:
        c = r["c"]
        print(f"\n[{r['cid']}] {c['name']}（{c['industry']}）")
        if r["state"]:
            color = "绿" if r["buf"] == 0 else ("黄" if r["buf"] <= 2 else "红")
            print(f"  状态机: {r['state']} ｜ buffer: {r['buf']}（{color}）" + (f" ｜ 挂起等: {r['hang']}" if r["hang"] else ""))
        print(f"  定位:{'✅' if r['positioned'] else '❌ 待填'}  选题:{r['n_topics']}条  脚本:{r['n_scripts']}条  回标:{r['n_tagged']}条")
        print(f"  当前缺口: {r['gap']}  →  建议下一步: {r['nxt']}")


# ---------------- state（运行状态，v2 新增） ----------------

STATE_FILE = "05-state.md"
SCHEMA_VERSION = 3


def state_repl(body, field, value):
    return re.sub(rf"^- {field}：.*$", f"- {field}：{value}", body, flags=re.M)


def get_buffer(body):
    m = re.search(r"^- buffer（已拍未发）：(\d+)", body, re.M)
    return int(m.group(1)) if m else 0


def cmd_state(cid, set_kv=None):
    cdir = os.path.join(CLIENTS, cid)
    sp = os.path.join(cdir, STATE_FILE)
    if not os.path.exists(sp):
        print(f"clients/{cid}/{STATE_FILE} 不存在；先跑 onboard {cid} ...")
        return
    body = open(sp, encoding="utf-8").read()
    if not set_kv:
        cur = re.search(r"^- 状态机：(.+)$", body, re.M)
        step = re.search(r"^- 当前步：(.+)$", body, re.M)
        upd = re.search(r"^- 上次更新：(.+)$", body, re.M)
        aha = re.search(r"^- 当前 Aha 判级：(.+)$", body, re.M)
        hang = re.search(r"^- 等什么：(.+)$", body, re.M)
        buf = get_buffer(body)
        buf_color = "绿" if buf == 0 else ("黄" if buf <= 2 else "红")
        print(f"[{cid}] 状态: {cur.group(1).strip() if cur else '未填'}")
        print(f"  当前步: {step.group(1).strip() if step else '-'} ｜ 更新: {upd.group(1).strip() if upd else '-'}")
        print(f"  Aha判级: {aha.group(1).strip() if aha else '-'} ｜ 挂起等: {hang.group(1).strip() if hang else '无'}")
        print(f"  buffer(已拍未发): {buf}（{buf_color}）")
        traj = re.findall(r"^-\s*\d{4}-\d{2}-\d{2}.*$", body, re.M)
        if traj:
            print("  轨迹:")
            for t in traj[-5:]:
                print(f"    {t}")
        return
    today = datetime.date.today().isoformat()
    def repl(field, value):
        nonlocal body
        body = re.sub(rf"^- {field}：.*$", f"- {field}：{value}", body, flags=re.M)
    if set_kv.get("state"):
        repl("状态机", set_kv["state"])
    if set_kv.get("step"):
        repl("当前步", set_kv["step"])
    repl("上次更新", today)
    evt = set_kv.get("event", "手动更新")
    body = body.rstrip() + f"\n- {today} {evt} → {set_kv.get('state', '（状态未变）')}\n"
    open(sp, "w", encoding="utf-8").write(body)
    print(f"✅ {cid} 运行状态已更新：{set_kv.get('state', '-')}")


# ---------------- v3：predict / shoot / publish / retro / recommend / bump / persona / migrate ----------------

def pred_dir(cid):
    return os.path.join(CLIENTS, cid, "predictions")


def pred_path(cid, slug, today=None):
    d = today or datetime.date.today().isoformat()
    return os.path.join(pred_dir(cid), f"{d}_{slug}.md")


def state_read(cid):
    sp = os.path.join(CLIENTS, cid, STATE_FILE)
    if not os.path.exists(sp):
        return None, None
    return sp, open(sp, encoding="utf-8").read()


def state_write(cid, body, event, note):
    sp = os.path.join(CLIENTS, cid, STATE_FILE)
    today = datetime.date.today().isoformat()
    body = state_repl(body, "上次更新", today)
    body = body.rstrip() + f"\n- {today} {event} → {note}\n"
    open(sp, "w", encoding="utf-8").write(body)


def buffer_set(cid, delta, event):
    sp, body = state_read(cid)
    if body is None:
        print(f"clients/{cid}/{STATE_FILE} 不存在；先 onboard。")
        sys.exit(1)
    buf = max(0, get_buffer(body) + delta)
    body = state_repl(body, "buffer（已拍未发）", str(buf))
    color = "绿" if buf == 0 else ("黄" if buf <= 2 else "红")
    state_write(cid, body, event, f"buffer={buf}（{color}）")
    if buf >= 3:
        print(f"  警告：buffer={buf} 红灯，停止新拍摄，先发布库存。")
    return buf


def cmd_predict(cid, slug):
    os.makedirs(pred_dir(cid), exist_ok=True)
    pp = pred_path(cid, slug)
    if os.path.exists(pp):
        print(f"预测已存在且不可改：{pp}")
        print("要修正请新开 _redo 文件（原版必须保留）：", pp.replace(".md", "_redo.md"))
        sys.exit(1)
    tpl = os.path.join(TPL, "prediction-template.md")
    body = open(tpl, encoding="utf-8").read() if os.path.exists(tpl) else "# 预测\n"
    body = body.replace("{{CLIENT_ID}}", cid).replace("{{TOPIC}}", slug)\
               .replace("{{DATE}}", datetime.date.today().isoformat())
    open(pp, "w", encoding="utf-8").write(body)
    sp, sb = state_read(cid)
    if sb:
        state_write(cid, sb, f"盲预测建档 {slug}", "预测已写（immutable）")
    print(f"✅ 盲预测已建档：{pp}")
    print("填写 ## 预测 段（必须在看到任何实际数据之前）；写完即不可改。")


def cmd_shoot(cid, slug):
    has_pred = False
    if os.path.isdir(pred_dir(cid)):
        has_pred = any(f.endswith(f"_{slug}.md") for f in os.listdir(pred_dir(cid)))
    if not has_pred:
        print(f"未找到 {slug} 的预测文件——先 predict 再 shoot（预测必须先于拍摄）。")
        sys.exit(1)
    buf = buffer_set(cid, +1, f"已拍 {slug}")
    print(f"✅ {cid} 已拍未发 +1（buffer={buf}）")


def cmd_publish(cid, slug):
    buf = buffer_set(cid, -1, f"已发 {slug}")
    print(f"✅ {cid} 已发布登记（buffer={buf}）")
    print("下一步：发布后约 3 天跑 retro 追加复盘段。")


def cmd_retro(cid, slug):
    cands = []
    if os.path.isdir(pred_dir(cid)):
        cands = [f for f in os.listdir(pred_dir(cid)) if f.endswith(f"_{slug}.md")]
    if not cands:
        print(f"未找到 {slug} 的预测文件。")
        sys.exit(1)
    pp = os.path.join(pred_dir(cid), cands[0])
    body = open(pp, encoding="utf-8").read()
    if "已复盘" in body:
        print("该预测已复盘过；只允许补充数据，不允许改预测段。")
    today = datetime.date.today().isoformat()
    block = (f"\n### 复盘 {today}（已复盘）\n\n"
             "- 实际数据：播放 __ ｜ 完播 __% ｜ 赞 __ ｜ 藏 __ ｜ 转 __ ｜ 评 __ ｜ 线索 __\n"
             "- 偏差分析（预测 vs 实际）：\n"
             "- 复用结论（验证了/推翻了什么）：\n"
             "- Aha 判级：A / B / C（对照近 10 条均值基准线）\n")
    if "## 复盘" in body:
        body = body.rstrip() + "\n" + block
    else:
        body = body.rstrip() + f"\n\n## 复盘\n{block}"
    open(pp, "w", encoding="utf-8").write(body)
    sp, sb = state_read(cid)
    if sb:
        state_write(cid, sb, f"复盘 {slug}", "回标完成")
    print(f"✅ 复盘段已追加（只追加，未动预测段）：{pp}")


def cmd_recommend(cid):
    sp, body = state_read(cid)
    buf = get_buffer(body) if body else 0
    color = "绿" if buf == 0 else ("黄" if buf <= 2 else "红")
    print(f"[{cid}] buffer={buf}（{color}）")
    if buf >= 3:
        print("红灯：不推荐新选题。先发布库存，buffer 降到 2 以下再来。")
        return
    tp = os.path.join(CLIENTS, cid, "01-topics.md")
    pool = []
    if os.path.exists(tp):
        text = open(tp, encoding="utf-8").read()
        # 选题池里状态为「候选」的 ### 选题
        for m in re.finditer(r"^###\s+(.+?)\n(.*?)(?=^###|\Z)", text, re.M | re.S):
            title, body = m.group(1).strip(), m.group(2)
            if "[" in title:
                continue
            if "状态：候选" in body:
                pool.append(title)
        # 候选区里 trends 格式的待评行：- [YYYY-MM-DD] 候选句 ｜ 状态：待评
        for line in text.splitlines():
            ls = line.strip()
            if re.match(r"^- \[\d{4}-\d{2}-\d{2}\]", ls) and "待评" in ls:
                pool.append(ls)
    if not pool:
        print("候选池为空。先 matrix/assemble 出题，或按 references/trends-and-candidates.md 补候选。")
        return
    stable = pool[0]
    print(f"稳健推荐（已验证方向）：{stable}")
    if buf == 0 and len(pool) > 1:
        print(f"实验推荐（新角度）：{pool[-1]}")
    elif buf > 0:
        print("黄灯：只推 1 条稳健；先发库存再加实验。")


def cmd_bump(cid):
    scripts = os.path.join(CLIENTS, cid, "02-scripts.md")
    if not os.path.exists(scripts):
        print(f"无 {scripts}——先积累带「实际数据」的回标样本（≥5 条）再 bump。")
        sys.exit(1)
    text = open(scripts, encoding="utf-8").read()
    samples = re.findall(r"^###\s+\[(.*?)\]\s*(.*?)$(.*?)(?=^###|\Z)", text, re.M | re.S)
    done = [(d, t, b) for d, t, b in samples if re.search(r"实际数据：[^\n]*\d", b)]
    if len(done) < 5:
        print(f"校准池不足：仅 {len(done)} 条有回标数据（需 ≥5）。")
        sys.exit(1)
    out = os.path.join(CLIENTS, cid, f"bump-worksheet-{datetime.date.today().isoformat()}.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"# {cid} · 标准卡 bump 工作表（{datetime.date.today()}）\n\n")
        f.write("> 协议见 references/bump-protocol.md：新公式对全部样本重打分→排序一致性≥4/5→独立审核→写入 06-standard.md。\n\n")
        f.write("| 样本 | 旧公式分 | 新公式分 | 实际表现档(高/中/低) | 排序是否一致 |\n| --- | --- | --- | --- | --- |\n")
        for d, t, b in done:
            f.write(f"| {d} {t.strip()} |  |  |  |  |\n")
        f.write("\n## 校验\n\n- 排序一致样本数：__/总 __（需 ≥4/5）\n- 独立审核方：\n- 结论：通过 / 拒绝\n")
    print(f"✅ bump 工作表已生成（{len(done)} 条校准样本）：{out}")
    print("填完校验段；不通过则保留旧版标准卡。")


def cmd_persona(cid):
    scripts = os.path.join(CLIENTS, cid, "02-scripts.md")
    signals = []
    if os.path.exists(scripts):
        for m in re.finditer(r"实际数据：[^\n]*评[^\n]*?(\d+)[^\n]*", open(scripts, encoding="utf-8").read()):
            signals.append(m.group(0))
    tpl = os.path.join(TPL, "audience.md")
    body = open(tpl, encoding="utf-8").read() if os.path.exists(tpl) else "# 受众画像\n"
    body = body.replace("{{CLIENT_NAME}}", cid).replace("{{DATE}}", datetime.date.today().isoformat())
    out = os.path.join(CLIENTS, cid, "audience.md")
    if not os.path.exists(out):
        open(out, "w", encoding="utf-8").write(body)
    print(f"✅ 画像骨架就位：{out}")
    print(f"从回标中抽到 {len(signals)} 条评论信号；请由 Agent 聚类分析后填画像（盲评上下文不得读本文件）。")


def cmd_migrate(cid=None):
    targets = [cid] if cid else list(load_registry().keys())
    if not targets:
        print("没有客户。先 onboard。")
        return
    new_files = {"05-state.md": "running-state.md", "06-standard.md": "standard-card.md"}
    for c in targets:
        cdir = os.path.join(CLIENTS, c)
        if not os.path.isdir(cdir):
            continue
        reg = load_registry().get(c, {})
        for target, tpl in new_files.items():
            tp = os.path.join(cdir, target)
            if not os.path.exists(tp):
                src = os.path.join(TPL, tpl)
                body = open(src, encoding="utf-8").read() if os.path.exists(src) else f"# {target}\n"
                body = body.replace("{{CLIENT_ID}}", c).replace("{{CLIENT_NAME}}", reg.get("name", c))\
                           .replace("{{INDUSTRY}}", reg.get("industry", "")).replace("{{CTA}}", reg.get("cta", ""))\
                           .replace("{{DATE}}", datetime.date.today().isoformat())
                open(tp, "w", encoding="utf-8").write(body)
                print(f"  + {c}/{target}")
        sp = os.path.join(cdir, STATE_FILE)
        if os.path.exists(sp):
            body = open(sp, encoding="utf-8").read()
            if "- schema：" not in body:
                body = body.replace("## 状态快照\n", f"## 状态快照\n\n- schema：{SCHEMA_VERSION}\n", 1)
                open(sp, "w", encoding="utf-8").write(body)
        print(f"✅ {c} 已迁移到 schema v{SCHEMA_VERSION}")


# ---------------- check（文案三关校验，v3.1 新增） ----------------

BANNED_STRICT = ["进行", "实施", "开展", "针对", "关于", "由于", "因此", "一定要", "必须要", "应该要",
                 "需要注意的是", "所谓", "予以", "给予", "能够", "可以说", "在于", "对于", "通过", "使得"]
BANNED_SOFT = ["其", "之", "而", "则", "即", "亦"]
PERSONA_WARN = ["我们", "人们", "一个人"]
GOOD_OPENERS = ["记住", "真正的", "一个残酷的真相", "别再", "停止", "从今天起", "听好了", "醒醒吧"]
BAD_OPENERS = ["你知道吗", "你有没有想过", "你是否", "今天我们来聊聊", "很多人不知道", "其实"]
ACTION_WORDS = ["学习", "研究", "重复", "实践", "观察", "放下", "开始", "练习", "尝试", "改变", "停止", "接受", "拒绝", "专注"]
BAD_ENDINGS = ["去吧", "加油吧", "相信自己吧", "你会变得更好", "一切都会好起来"]
COMPLIANCE_WORDS = ["必治", "包就业", "包考证", "月入过万", "稳赚", "百分百", "保证赚钱", "绝对有效",
                    "不要划走", "宇宙选中你", "马上发财", "必然转运", "治病", "长寿", "提高免疫力",
                    "国家级", "最高级", "最佳", "全网第一", "行业第一", "销量第一", "排名第一", "100%"]
PUNCT = "，。！？；：、,.!?;:\"'“”‘’（）()【】《》…—-· \t"


def sent_len(s):
    return len([c for c in s if c not in PUNCT])


def load_calibration(cid):
    """读 clients/<cid>/06-standard.md 的「机判校准」区（v3.4：客户成片实测校准，优先于通用规则）。
    区格式（勿手改行格式）：
    ## 机判校准（check --client 读取）
    - max_sentence_len: 54        # 硬线上限（字）；无则用通用 15
    - action_words: 要/看/对/查    # 客户动词表；无则用通用表
    - good_openers: 能不能把|最近   # 客户合格开头；|分隔；无则用通用表
    - good_closers: 评论区打|我帮你 # 客户收尾锚点；无则用通用规则
    """
    sp = os.path.join(CLIENTS, cid, "06-standard.md")
    if not os.path.exists(sp):
        return None
    body = open(sp, encoding="utf-8").read()
    m = re.search(r"##\s*机判校准[^\n]*\n(.*?)(?=\n##|\Z)", body, re.S)
    if not m:
        return None
    cal = {}
    for line in m.group(1).splitlines():
        mm = re.match(r"^-\s*(max_sentence_len|action_words|good_openers|good_closers)\s*[:：]\s*(.+)$", line.strip())
        if mm:
            key, val = mm.group(1), mm.group(2).strip()
            if key == "max_sentence_len":
                try:
                    cal[key] = int(val)
                except ValueError:
                    pass
            else:
                if val:
                    cal[key] = val
    return cal or None


def cmd_check(path, cid=None):
    cal = load_calibration(cid) if cid else None
    cal_note = f"（客户化校准：{cid}，句长上限 {cal.get('max_sentence_len')} 字）" if cal else "（通用规则）"
    max_len = cal.get("max_sentence_len", 15) if cal else 15
    action_words = cal.get("action_words", "") if cal else ""
    act_list = action_words.split("/") if action_words else ACTION_WORDS
    good_open = cal.get("good_openers", "") if cal else ""
    good_open_list = good_open.split("|") if good_open else GOOD_OPENERS
    good_close = cal.get("good_closers", "") if cal else ""
    raw = open(path, encoding="utf-8").read()
    m = re.search(r"####\s*脚本\s*\n(.*?)(?=\n####|\n###|\Z)", raw, re.S)
    text = m.group(1) if m else raw
    sents = []
    for ln in text.splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("|") or ln.startswith("#"):
            continue
        ln = re.sub(r"^[-*>\s]+", "", ln)
        ln = re.sub(r"^[^：:]{2,12}（[^）]*）[:：]", "", ln)  # 去掉卡片行内标签
        for s in re.split(r"[。！？!?；;…]+", ln):
            s = s.strip(PUNCT)
            if s:
                sents.append(s)
    if not sents:
        print("未解析到文案句子。可以直接传纯文案文件，或脚本卡（取 #### 脚本 段）。")
        sys.exit(1)
    fmt_fail, fmt_warn, str_fail, str_warn = [], [], [], []
    for i, s in enumerate(sents, 1):
        n = sent_len(s)
        if n > max_len:
            segs = [x for x in re.split(r"[，,、]", s) if x.strip(PUNCT)]
            lianji = not cal and n <= 24 and len(segs) >= 2 and all(sent_len(x) <= 8 for x in segs)
            if not lianji:
                fmt_fail.append(f"第{i}句超 {max_len} 字（{n}字）：{s}")
        for w in BANNED_STRICT:
            if w in s:
                fmt_fail.append(f"第{i}句含书面禁用词「{w}」：{s}")
        for w in BANNED_SOFT:
            if w in s:
                fmt_warn.append(f"第{i}句疑似文言单字「{w}」（人工复核）：{s}")
        for w in PERSONA_WARN:
            if w in s:
                fmt_warn.append(f"第{i}句人称建议改「你/自己」（含「{w}」）：{s}")
    first, last = sents[0], sents[-1]
    if any(first.startswith(w) for w in BAD_OPENERS):
        str_fail.append(f"开头用禁用词：{first}")
    elif not any(first.startswith(w) for w in good_open_list):
        label = "（通用）记住/真正的/别再/醒醒吧" if not good_open else "（客户成片实测）"
        str_warn.append(f"开头未见合格开头词 {label}：{first}")
    n_actions = sum(1 for w in act_list if any(w in s for s in sents))
    if n_actions < 2:
        str_fail.append(f"具体动作词不足（{n_actions}个，需≥2）：{'/'.join(act_list[:6])}…")
    if any(w in last for w in BAD_ENDINGS):
        str_fail.append(f"收尾是空洞鸡汤：{last}")
    elif good_close:
        if not any(c in last for c in good_close.split("|")):
            str_warn.append(f"收尾未见客户化行动锚点（{good_close}）：{last}")
    elif not ("先从" in last and "开始" in last) and "记住" not in last and "开始" not in last:
        str_warn.append(f"收尾未见「先从X开始」式行动锚点：{last}")
    comp_fail = []
    for i, s in enumerate(sents, 1):
        for w in COMPLIANCE_WORDS:
            if w in s:
                comp_fail.append(f"第{i}句含合规违禁词「{w}」：{s}")
    print(f"== 文案三关校验：{path} {cal_note} ==")
    print(f"\n【第一关·格式】{'✅ 通过' if not fmt_fail else '❌ 未过'}")
    for x in fmt_fail:
        print(f"  ❌ {x}")
    for x in fmt_warn:
        print(f"  ⚠️ {x}")
    print(f"\n【第二关·结构】{'✅ 通过' if not str_fail else '❌ 未过'}")
    for x in str_fail:
        print(f"  ❌ {x}")
    for x in str_warn:
        print(f"  ⚠️ {x}")
    print("\n【第三关·逻辑】（三关系检查法，需 Agent/人判断）")
    print("  逐对相邻句检查：原因（因为B所以A）/ 结果（因为A所以B）/ 具体化（A具体来说就是B），三者至少其一：")
    for i, s in enumerate(sents, 1):
        print(f"  {i}. {s}")
    print(f"\n【合规扫描】{'✅ 无违禁词' if not comp_fail else '❌ 命中违禁词'}")
    for x in comp_fail:
        print(f"  ❌ {x}")
    ok = not fmt_fail and not str_fail and not comp_fail
    print(f"\n结论：{'✅ 前两关通过，请完成第三关逐对检查' if ok else '❌ 按上述条目修改后重跑 check'}")


# ---------------- v3.3：aha / patrol / schedule / seed / archive + metrics 预测精度 ----------------

def parse_num(s):
    """解析 '5000' / '3.2万' / '5w' 为数值。"""
    m = re.search(r"([\d.]+)\s*([万wW]?)", s)
    if not m:
        return None
    v = float(m.group(1))
    if m.group(2):
        v *= 10000
    return v


def script_entries(cid):
    """解析 02-scripts.md 的条目：(日期, 选题名, 钩子号或None, 播放或None, 正文)。"""
    sp = os.path.join(CLIENTS, cid, "02-scripts.md")
    if not os.path.exists(sp):
        return []
    text = open(sp, encoding="utf-8").read()
    out = []
    for m in re.finditer(r"^###\s+\[(.*?)\]\s*(.*?)$(.*?)(?=^###|\Z)", text, re.M | re.S):
        d, t, b = m.group(1), m.group(2).strip(), m.group(3)
        hook = re.search(r"钩子体：第\s*(\d+)\s*类", b)
        play = re.search(r"实际数据：[^\n]*?播放\s*([\d.]+\s*[万wW]?)", b)
        out.append((d, t, int(hook.group(1)) if hook else None,
                    parse_num(play.group(1)) if play else None, b))
    return out


def cmd_aha(cid):
    entries = [(d, t, p) for d, t, h, p, b in script_entries(cid) if p]
    if len(entries) < 3:
        print(f"[{cid}] 回标样本不足（{len(entries)} 条有播放数据，需 ≥3）——先积累回标。")
        return
    plays = [p for _, _, p in entries]
    window = plays[-10:]
    baseline = sum(window) / len(window)
    print(f"[{cid}] Aha 判级（基准线=近{len(window)}条均值 {baseline:.0f} 播放）\n")
    hot = []
    for d, t, p in entries:
        ratio = p / baseline if baseline else 0
        tag = "🔥 超基线" if ratio >= 1.5 else ("✓ 达标" if ratio >= 0.8 else "· 低于基线")
        if ratio >= 1.5:
            hot.append((d, t, ratio))
        print(f"  [{d}] {t[:24]}：{p:.0f}（{ratio:.1f}x）{tag}")
    print()
    recent2 = plays[-2:]
    if len(hot) >= 2:
        print(f"建议判级：A 级候选（{len(hot)} 条超基线）——再确认评论/转化强反馈后进拍穿计划。")
        for d, t, r in hot:
            print(f"  拍穿种子：[{d}] {t[:24]}（{r:.1f}x）")
    elif len(recent2) == 2 and all(p < baseline * 0.8 for p in recent2):
        print("建议判级：C 级——连续 2 轮低于基准线，归档当前假设，换方向冷启动。")
    elif hot:
        print("建议判级：B 级——有单条超基线但不稳，改钩子/换场景再测 3 条。")
    else:
        print("建议判级：未出 Aha 信号——继续按缺口清单补素材测试。")


def cmd_patrol():
    reg = load_registry()
    if not reg:
        print("没有客户。")
        return
    today = datetime.date.today()
    print(f"== 每日巡检（{today}）==")
    any_issue = False
    for cid, c in reg.items():
        if c.get("archived"):
            continue
        issues = []
        sp, body = state_read(cid)
        if body:
            buf = get_buffer(body)
            if buf >= 3:
                issues.append(f"🔴 buffer={buf} 红灯，先发布库存")
            hang = re.search(r"^- 等什么：(.+)$", body, re.M)
            if hang and hang.group(1).strip():
                upd = re.search(r"^- 上次更新：(\d{4}-\d{2}-\d{2})", body, re.M)
                days = (today - datetime.date.fromisoformat(upd.group(1))).days if upd else 0
                overdue = "（超期≥15天，转待决策）" if days >= 15 else f"（已等 {days} 天）"
                issues.append(f"⏸ 挂起等「{hang.group(1).strip()}」{overdue}")
        pdir = pred_dir(cid)
        if os.path.isdir(pdir):
            for f in sorted(os.listdir(pdir)):
                if not f.endswith(".md") or f.endswith("_redo.md"):
                    continue
                pbody = open(os.path.join(pdir, f), encoding="utf-8").read()
                if "已复盘" not in pbody:
                    fdate = f[:10]
                    try:
                        days = (today - datetime.date.fromisoformat(fdate)).days
                    except ValueError:
                        days = 0
                    if days >= 3:
                        issues.append(f"📈 待复盘：{f}（预测已 {days} 天）")
        noshoot = re.findall(r"状态：已发布", open(os.path.join(CLIENTS, cid, "02-scripts.md"), encoding="utf-8").read()) if os.path.exists(os.path.join(CLIENTS, cid, "02-scripts.md")) else []
        tagged = len(re.findall(r"实际数据：[^\n]*\d", open(os.path.join(CLIENTS, cid, "02-scripts.md"), encoding="utf-8").read())) if os.path.exists(os.path.join(CLIENTS, cid, "02-scripts.md")) else 0
        if len(noshoot) > tagged:
            issues.append(f"📊 待回标：{len(noshoot) - tagged} 条已发布无数据")
        if issues:
            any_issue = True
            print(f"\n[{cid}] {c['name']}")
            for i in issues:
                print(f"  {i}")
    if not any_issue:
        print("\n全部客户无待办异常。")


def cmd_schedule(cid):
    hooks = [h for d, t, h, p, b in script_entries(cid) if h]
    if not hooks:
        print(f"[{cid}] 脚本库无钩子标注。")
        return
    CONFLICT = {1, 2, 7, 10, 11, 22}
    TRUST = {4, 12, 15, 17, 18, 20, 23}
    print(f"[{cid}] 排期纪律检查（共 {len(hooks)} 条已标钩子）")
    bad = False
    for i in range(len(hooks) - 2):
        win = hooks[i:i + 3]
        if len(set(win)) == 1 and win[0] in CONFLICT:
            print(f"  ❌ 第{i+1}-{i+3}条连续重复对立冲突钩子（第{win[0]}类）")
            bad = True
        elif all(h in CONFLICT for h in win):
            print(f"  ⚠️ 第{i+1}-{i+3}条全为对立冲突类钩子（{win}），建议插入信任实证类")
            bad = True
    trust_ratio = sum(1 for h in hooks if h in TRUST) / len(hooks)
    mark = "✅" if trust_ratio >= 0.4 else "❌"
    print(f"  {mark} 信任实证类占比 {trust_ratio:.0%}（目标 ≥40%）")
    if not bad and trust_ratio >= 0.4:
        print("  ✅ 排期纪律全部通过")


def cmd_seed(cid):
    cdir = os.path.join(CLIENTS, cid)
    mj = os.path.join(cdir, "matrix.json")
    if not os.path.exists(mj):
        print(f"缺 clients/{cid}/matrix.json——先 onboard 再填词表。")
        sys.exit(1)
    cfg = json.load(open(mj, encoding="utf-8"))
    core, related, personas = cfg["core"], cfg["related"], cfg["personas"]
    if any("填" in w for w in [core] + related + personas):
        print("matrix.json 还是模板状态，先填真实词表。")
        sys.exit(1)
    pains = ["怎么办", "避坑", "多少钱", "怎么选", "区别", "靠谱吗"]
    out = os.path.join(cdir, f"seed-search-{datetime.date.today().isoformat()}.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"# {cid} · 冷启动搜索任务清单（{datetime.date.today()}）\n\n")
        f.write("> 用法：逐条搜索，结果只提取「真实需求/常见误区/典型案例」三类，标来源链接，进 01-topics.md 候选区（状态：待评）。不脑补。\n\n")
        f.write("## 关键词 × 痛点词\n\n")
        n = 0
        for r in related[:8]:
            for p in pains[:3]:
                n += 1
                f.write(f"- [ ] `{core} {r} {p}`\n")
        f.write("\n## 人群场景 × 行业核心\n\n")
        for pe in personas[:6]:
            n += 1
            f.write(f"- [ ] `{pe} {core}`\n")
    print(f"✅ {cid}: {n} 条搜索任务 -> {out}")


def cmd_archive(cid):
    cdir = os.path.join(CLIENTS, cid)
    if not os.path.isdir(cdir):
        print(f"客户 {cid} 不存在。")
        sys.exit(1)
    adir = os.path.join(CLIENTS, "_archive")
    os.makedirs(adir, exist_ok=True)
    reg = load_registry()
    if cid in reg:
        reg[cid]["archived"] = True
        save_registry(reg)
    sp, body = state_read(cid)
    if body:
        state_write(cid, body, "归档", "合作终止/长期待决策")
    os.rename(cdir, os.path.join(adir, cid))
    print(f"✅ {cid} 已归档到 clients/_archive/{cid}（registry 标记 archived）")


# ---------------- 钩子库解析 + assemble ----------------

def parse_hooks():
    text = open(HOOK, encoding="utf-8").read()
    parts = re.split(r'\n## (\d+)\.\s*', text)
    hooks = []
    for i in range(1, len(parts) - 1, 2):
        num = int(parts[i])
        body = re.split(r'\n## ', parts[i + 1])[0]
        first = body.split('\n', 1)[0].strip()
        hook_type = re.split(r'（', first)[0].strip()
        generic = ""
        for line in body.split('\n'):
            m = re.match(r'^-\s*通用[：:][「『](.+?)[」』]\s*$', line.strip())
            if m:
                generic = m.group(1)
        hooks.append({"num": num, "type": hook_type, "generic": generic})
    return hooks


def cmd_assemble(cid):
    reg = load_registry()
    if cid not in reg:
        print(f"客户 {cid} 不存在，先 onboard。")
        sys.exit(1)
    c = reg[cid]
    hooks = [h for h in parse_hooks() if h["generic"]]
    cdir = os.path.join(CLIENTS, cid)
    out = os.path.join(cdir, "auto-topics.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"# {c['name']} · 钩子装配选题候选（{datetime.date.today()}）\n\n")
        f.write(f"> 共 {len(hooks)} 条（钩子库通用示例装配）。**必须逐条替换为客户真实痛点后再用**，"
                f"并过评分闸门（references/scoring-gate.md，≥11 分才进排期）。\n\n")
        f.write("| # | 钩子类型 | 流量场景 | 通用开头句（待本地化） | 转化动作 |\n| ---: | --- | --- | --- | --- |\n")
        for h in hooks:
            f.write(f"| {h['num']} | {h['type']} | 推荐页 | {h['generic']} | {c['cta']} |\n")
    print(f"✅ {cid}: {len(hooks)} 条候选 -> {out}")
    print("提醒：这些是通用句，本地化改写后逐条过评分闸门（python director.py score）。")


# ---------------- matrix ----------------

def llm_expand(core, related, personas):
    base, key, model = (os.environ.get("TOPIC_LLM_BASE_URL", "").rstrip("/"),
                        os.environ.get("TOPIC_LLM_API_KEY", ""),
                        os.environ.get("TOPIC_LLM_MODEL", ""))
    if not (base and key and model):
        return None
    import urllib.request
    prompt = (f"行业核心「{core}」。已知行业相关词: {related}；人群/场景: {personas}。"
              "请各补充 5 个新词(不重复、贴近真实获客场景)，只输出 JSON: {\"related\":[...],\"personas\":[...]}")
    req = urllib.request.Request(
        base + "/chat/completions",
        data=json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}],
                         "temperature": 0.7}).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            content = json.load(r)["choices"][0]["message"]["content"]
        m = re.search(r'\{.*\}', content, re.S)
        return json.loads(m.group(0)) if m else None
    except Exception as e:
        print(f"  [llm] 调用失败，回退规则引擎: {e}")
        return None


def cmd_matrix(cid, use_llm):
    cdir = os.path.join(CLIENTS, cid)
    mp = os.path.join(cdir, "matrix.json")
    if not os.path.exists(mp):
        print(f"缺 clients/{cid}/matrix.json——先 onboard 再填词表（词表只能来自采访原话/评论区/搜索联想）。")
        sys.exit(1)
    cfg = json.load(open(mp, encoding="utf-8"))
    core, related, personas = cfg["core"], cfg["related"], cfg["personas"]
    if any("填" in w for w in [core] + related + personas):
        print("matrix.json 还是模板状态，请先填真实词表（不编造客户事实）。")
        sys.exit(1)
    if use_llm:
        ext = llm_expand(core, related, personas)
        if ext:
            related += [w for w in ext.get("related", []) if w not in related]
            personas += [w for w in ext.get("personas", []) if w not in personas]
            print(f"  [llm] 词表扩充 -> 相关 {len(related)} / 人群场景 {len(personas)}")
    combos = list(itertools.product(related, personas))
    out = os.path.join(cdir, "matrix-topics.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"# {cid} · 连连看需求组合选题池（{datetime.date.today()}）\n\n")
        f.write(f"> 行业核心「{core}」× 行业相关({len(cfg['related'])}) × 人群/场景({len(cfg['personas'])}) = **{len(combos)}** 条组合。\n")
        f.write("> 这是「选什么题」层：先按 references/scoring-gate.md 过评分闸门，≥11 分的再到选题卡定钩子/流量场景。\n\n")
        f.write("| # | 需求组合 | 候选选题句 | 建议流量场景 |\n| ---: | --- | --- | --- |\n")
        for i, (r, p) in enumerate(combos, 1):
            topic = f"{p}遇到「{core}·{r}」问题怎么办"
            scene = "搜索页" if any(k in r for k in ("怎么", "如何", "教程", "流程", "价格", "型号", "清单")) else "推荐页"
            f.write(f"| {i} | {core} × {r} × {p} | {topic} | {scene} |\n")
    print(f"✅ {cid}: {len(combos)} 条组合 -> {out}")


# ---------------- score（交互式评分闸门） ----------------

ITEMS = [("人群清晰", "明确到角色/场景/付费时刻=2"), ("痛点具体", "客户正在发生的高痛问题=2"),
         ("钩子强度", "钩子体×痛点严丝合缝（搜索页看搜索词/白描看真实细节）=2"),
         ("普通人可懂", "一秒听懂「这跟我有关」=2"), ("判断标准/产物", "有可执行清单或可收藏产物=2"),
         ("信任证据", "现场/案例/数据/流程=2"), ("线索入口", "明确关键词+下一步材料=2"),
         ("合规/平台风险", "无违禁夸大=2")]

def cmd_score():
    print("== 选题评分闸门（8 项 × 0-2 分，≥11 进排期）==")
    print("逐条输入 0/1/2 并回车；q 退出。\n")
    topic = input("选题一句话：").strip()
    if not topic or topic == "q":
        return
    total = 0
    for name, hint in ITEMS:
        while True:
            v = input(f"  {name}（{hint}）：").strip()
            if v == "q":
                return
            if v in ("0", "1", "2"):
                total += int(v)
                break
            print("    只接受 0/1/2")
    rank = "S 级（≥14，重点磨）" if total >= 14 else ("A 级（11-13，可排期）" if total >= 11 else "B 级（<11，打回）")
    print(f"\n「{topic}」总分 {total}/16 → {rank}")
    if total >= 11:
        print("下一步：录入选题卡（templates/topic-card.md），定钩子体与流量场景。")
    else:
        print("打回：回到需求组合层重组（matrix），或换钩子/换痛点表达后重评。")


# ---------------- metrics ----------------

def cmd_metrics():
    reg = load_registry()
    if not reg:
        print("还没有客户数据。")
        return
    print("== 钩子联动指标 ==")
    for cid, c in reg.items():
        cdir = os.path.join(CLIENTS, cid)
        topics_p, scripts_p = os.path.join(cdir, "01-topics.md"), os.path.join(cdir, "02-scripts.md")
        t_text = open(topics_p, encoding="utf-8").read() if os.path.exists(topics_p) else ""
        s_text = open(scripts_p, encoding="utf-8").read() if os.path.exists(scripts_p) else ""
        topics = [b for b in re.split(r'\n###\s', t_text)[1:] if len(b.strip()) > 10 and not b.strip().startswith("[")]
        hooked = sum(1 for b in topics if "钩子" in b)
        scripts = [b for b in re.split(r'\n###\s', s_text)[1:] if "钩子" in b and not b.strip().startswith("[")]
        tagged = sum(1 for b in scripts if re.search(r'实际数据：[^\n]*\d', b))
        usage = {}
        for b in scripts:
            m = re.search(r'钩子体：第\s*(\d+)\s*类', b)
            if m:
                usage[int(m.group(1))] = usage.get(int(m.group(1)), 0) + 1
        cov = f"{hooked}/{len(topics)} = {hooked/len(topics):.0%}" if topics else "无选题"
        tag = f"{tagged}/{len(scripts)} = {tagged/len(scripts):.0%}" if scripts else "无脚本"
        print(f"\n[{cid}] {c['name']}")
        print(f"  钩子覆盖率: {cov}（目标 100%）")
        print(f"  回标率:     {tag}（目标 100%，无回标不归档）")
        print(f"  钩子用量:   {dict(sorted(usage.items())) or '（脚本未标钩子编号）'}")
        # v3.3 预测精度（盲预测 vs 实际）
        pdir = pred_dir(cid)
        preds = []
        if os.path.isdir(pdir):
            for f in sorted(os.listdir(pdir)):
                if not f.endswith(".md") or f.endswith("_redo.md"):
                    continue
                pb = open(os.path.join(pdir, f), encoding="utf-8").read()
                pe = re.search(r"预测表现：[^\n]*?播放约\s*([\d.]+\s*[万wW]?)", pb)
                ae = re.search(r"实际数据：[^\n]*?播放\s*([\d.]+\s*[万wW]?)", pb)
                if pe and ae:
                    pv, av = parse_num(pe.group(1)), parse_num(ae.group(1))
                    if pv and av:
                        preds.append((f[:10], pv, av))
        if preds:
            errs = [abs(pv - av) / av for _, pv, av in preds]
            print(f"  预测精度:   平均偏差 {sum(errs)/len(errs):.0%}（{len(preds)} 条有对照；收敛中更佳）")
            for d, pv, av in preds[-5:]:
                print(f"    [{d}] 预测 {pv:.0f} → 实际 {av:.0f}（偏差 {abs(pv-av)/av:.0%}）")
    print("\n北极星「钩子命中率」需回标数据积累后计算：某钩子体爆款数 ÷ 该钩子体用量。")


USAGE = __doc__

def _console_safe():
    """老 Windows GBK 控制台输出 emoji 不崩：无法编码的字符替换为 ?，中文不受影响。"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except Exception:
            pass

def main():
    _console_safe()
    args = [a for a in sys.argv[1:] if a != "--llm"]
    use_llm = "--llm" in sys.argv
    if not args:
        print(USAGE)
        return
    cmd = args[0]
    if cmd == "onboard" and len(args) >= 5:
        cmd_onboard(args[1], args[2], args[3], args[4])
    elif cmd == "status":
        cmd_status()
    elif cmd == "matrix" and len(args) >= 2:
        cmd_matrix(args[1], use_llm)
    elif cmd == "assemble" and len(args) >= 2:
        cmd_assemble(args[1])
    elif cmd == "score":
        cmd_score()
    elif cmd == "state" and len(args) >= 2:
        kv = None
        if len(args) > 2 and args[2] == "set":
            kv = {}
            it = iter(args[3:])
            for a in it:
                if a.startswith("--"):
                    kv[a[2:]] = next(it, "")
        cmd_state(args[1], kv)
    elif cmd == "predict" and len(args) >= 3:
        cmd_predict(args[1], args[2])
    elif cmd == "shoot" and len(args) >= 3:
        cmd_shoot(args[1], args[2])
    elif cmd == "publish" and len(args) >= 3:
        cmd_publish(args[1], args[2])
    elif cmd == "retro" and len(args) >= 3:
        cmd_retro(args[1], args[2])
    elif cmd == "recommend" and len(args) >= 2:
        cmd_recommend(args[1])
    elif cmd == "bump" and len(args) >= 2:
        cmd_bump(args[1])
    elif cmd == "persona" and len(args) >= 2:
        cmd_persona(args[1])
    elif cmd == "migrate":
        cmd_migrate(args[1] if len(args) > 1 else None)
    elif cmd == "aha" and len(args) >= 2:
        cmd_aha(args[1])
    elif cmd == "patrol":
        cmd_patrol()
    elif cmd == "schedule" and len(args) >= 2:
        cmd_schedule(args[1])
    elif cmd == "seed" and len(args) >= 2:
        cmd_seed(args[1])
    elif cmd == "archive" and len(args) >= 2:
        cmd_archive(args[1])
    elif cmd == "check" and len(args) >= 2:
        cid = None
        if "--client" in args:
            i = args.index("--client")
            if i + 1 < len(args):
                cid = args[i + 1]
        cmd_check(args[1], cid)
    elif cmd == "metrics":
        cmd_metrics()
    else:
        print(USAGE)
        sys.exit(1)


if __name__ == "__main__":
    main()
