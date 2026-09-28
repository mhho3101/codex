from pathlib import Path
import hashlib
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []
TEAM_CONTEXT_LEAK_MARKERS = [
    "老" + "大",
    "个人" + "包",
    "摄影" + "指导",
    "灯光" + "指导",
    "导演" + "知识库",
]


def require_file(relative: str) -> Path:
    path = ROOT / relative
    if not path.is_file():
        errors.append(f"missing file: {relative}")
    return path


def read(relative: str) -> str:
    path = require_file(relative)
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def require_text(label: str, text: str, values: list[str]) -> None:
    for value in values:
        if value not in text:
            errors.append(f"{label} missing: {value}")


def forbid_text(label: str, text: str, values: list[str]) -> None:
    for value in values:
        if value in text:
            errors.append(f"{label} contains forbidden text: {value}")


def text_block_after(label: str, text: str, marker: str) -> str:
    marker_index = text.find(marker)
    if marker_index < 0:
        errors.append(f"{label} missing marker: {marker}")
        return ""
    match = re.search(r"```text\r?\n(.*?)\r?\n```", text[marker_index:], re.DOTALL)
    if not match:
        errors.append(f"{label} missing text block after: {marker}")
        return ""
    return match.group(1)


def first_text_block(label: str, text: str) -> str:
    match = re.search(r"```text\r?\n(.*?)\r?\n```", text, re.DOTALL)
    if not match:
        errors.append(f"{label} missing first text block")
        return ""
    return match.group(1)


PRODUCTION_CARD_ONLY_LABELS = [
    "模型路由",
    "内部审查",
    "类型节奏",
    "类型、画幅、节奏与影调",
    "生产方式",
    "资产调用台账",
    "参考输入与权重",
    "空间与站位",
    "本段任务",
    "讲戏表/分镜头表执行台账",
    "岗位审查摘要",
]


def production_card_lines_in_model_body(text: str) -> list[str]:
    findings: list[str] = []
    for raw_line in text.splitlines():
        line = re.sub(r"^[#*+-]+\s*", "", raw_line.strip())
        for field in PRODUCTION_CARD_ONLY_LABELS:
            if re.match(rf"^(?:【)?{re.escape(field)}(?:】)?\s*[:：]", line):
                findings.append(raw_line.strip())
                break
    return findings


ALLOWED_TEAM_ROLE_NAMES = {
    "用户",
    "编剧",
    "资产提示词架构师",
    "视频提示词架构师",
}


def declared_execution_roles(skill_text: str) -> set[str]:
    match = re.search(
        r"^## 三个执行岗位\s*$\r?\n(.*?)(?=^##\s)",
        skill_text,
        re.MULTILINE | re.DOTALL,
    )
    if not match:
        return set()
    roles: set[str] = set()
    for role in re.findall(r"^\|\s*([^|]+?)\s*\|", match.group(1), re.MULTILINE):
        role = role.strip()
        if role not in {"岗位", "---"}:
            roles.add(role)
    return roles


def disallowed_explicit_role_declarations(text: str) -> list[str]:
    declared: list[str] = []
    patterns = [
        r"团队第[一二三四五六七八九十\d]+执行岗位\s*[:：]\s*([^，。；;\s]+)",
        r"新增([^，。；;\s]+)岗位",
    ]
    for pattern in patterns:
        for role in re.findall(pattern, text):
            if role not in ALLOWED_TEAM_ROLE_NAMES:
                declared.append(role)
    return declared


required = [
    "SKILL.md",
    "agents/openai.yaml",
    "团队用户操作说明.md",
    "references/团队故事板规则包/00_团队AI读取顺序.md",
    "references/团队故事板规则包/01_团队故事板与视频提示词执行方案.md",
    "references/团队故事板规则包/02_团队资产生成提示词规则.md",
    "references/团队故事板规则包/03_团队可分发提示词模板-执行版.md",
    "references/团队故事板规则包/04_团队故事板规则.md",
    "references/团队故事板规则包/05_编剧逻辑补充规则.md",
    "references/团队故事板规则包/07_讲戏表与分镜头表执行契约.md",
    "references/团队故事板规则包/资产提示词/00_资产输出总契约.md",
    "references/团队故事板规则包/资产提示词/01_人物9视图模板.md",
    "references/团队故事板规则包/资产提示词/01A_群像单张模板.md",
    "references/团队故事板规则包/资产提示词/02_场景单张五面空间模板.md",
    "references/团队故事板规则包/资产提示词/03_道具四宫格模板.md",
    "references/团队故事板规则包/资产提示词/04_特效四宫格模板.md",
    "references/团队故事板规则包/资产提示词/Midjourney V7/00_Midjourney V7资产路由与总契约.md",
    "references/团队故事板规则包/资产提示词/Midjourney V7/01_人物9视图模板.md",
    "references/团队故事板规则包/资产提示词/Midjourney V7/01A_群像单张模板.md",
    "references/团队故事板规则包/资产提示词/Midjourney V7/02_场景单张五面空间模板.md",
    "references/团队故事板规则包/资产提示词/Midjourney V7/03_道具四宫格模板.md",
    "references/团队故事板规则包/资产提示词/Midjourney V7/04_特效四宫格模板.md",
]
for item in required:
    require_file(item)

skill = read("SKILL.md")
router = read("references/团队故事板规则包/00_团队AI读取顺序.md")
asset_router = read("references/团队故事板规则包/02_团队资产生成提示词规则.md")
execution_plan = read("references/团队故事板规则包/01_团队故事板与视频提示词执行方案.md")
trigger_guide = read("references/团队故事板规则包/06_团队包使用说明与触发关键词.md")
user_guide = read("团队用户操作说明.md")
assets = read("references/团队故事板规则包/资产提示词/00_资产输出总契约.md")
video = read("references/团队故事板规则包/03_团队可分发提示词模板-执行版.md")
storyboard = read("references/团队故事板规则包/04_团队故事板规则.md")
logic = read("references/团队故事板规则包/05_编剧逻辑补充规则.md")

VIDEO_TEMPLATE_SHA256 = "64cff8eb1a6cc7ffc322211483b2911baa741c287ab83ef2039d37198b5285cc"
if hashlib.sha256(video.encode("utf-8")).hexdigest() != VIDEO_TEMPLATE_SHA256:
    errors.append("video template SHA256 does not match the locked team baseline")

for route in sorted(set(re.findall(r"`(references/[^`]+)`", skill))):
    if not (ROOT / route).exists():
        errors.append(f"SKILL route does not exist: {route}")

require_text(
    "version",
    skill,
    [
        "当前团队包版本为 `1.8.1`",
        "AI Film Team Storyboard 1.8.1",
    ],
)
require_text(
    "team execution boundary",
    skill + router + trigger_guide + user_guide + logic,
    [
        "只有用户明确要求",
        "没有明确要求补充逻辑时，不得修改剧本",
        "不提供小改剧本或大改剧本",
        "不生成完整分镜头表",
        "不生成顺场连续性表",
        "累计标黄",
        "Word 黄色突出显示",
    ],
)
forbid_text(
    "obsolete automatic logic behavior",
    skill + router + trigger_guide + user_guide + logic,
    [
        "没有编剧逻辑补充清单时先补最小生产衔接",
        "没有就先补最小生产衔接",
        "这段可以大改",
    ],
)
forbid_text(
    "team routing contradictions",
    router + execution_plan + asset_router + trigger_guide + user_guide + storyboard + logic,
    [
        "候选资产进入下游",
        "已淘汰资产进入下游",
        "资产交给故事板/视频：完整 `@集数-场次资产名`",
        "缺画面桥时先按 `05_编剧逻辑补充规则.md` 补齐",
        "编剧先补必要画面桥",
    ],
)
require_text(
    "versioned asset handoff",
    router + execution_plan + asset_router + trigger_guide + user_guide + storyboard,
    [
        "当前有效、已确认的完整 `@集数-场次资产名_Vn`",
        "填充无版本占位符时必须替换为已确认完整 `@集数-场次资产名_Vn`",
        "无授权时只核对并列出冲突/待确认，不新增或改写",
        "只有用户明确要求逻辑补充时才调用 `05_编剧逻辑补充规则.md`",
    ],
)
require_text(
    "team address",
    skill,
    [
        "用户是团队包唯一对话称呼",
        "每次回复均称呼“用户”",
        "不得用作本对话称谓",
        "仍需用户确认",
    ],
)
require_text(
    "team roles",
    skill,
    [
        "编剧",
        "资产提示词架构师",
        "视频提示词架构师",
        "只做单镜头分镜图",
        "已有确认分镜图，只做单镜头视频",
        "一镜一图一视频",
    ],
)

expected_execution_roles = ALLOWED_TEAM_ROLE_NAMES - {"用户"}
actual_execution_roles = declared_execution_roles(skill)
if actual_execution_roles != expected_execution_roles:
    errors.append(
        "team execution role declarations must equal allowlist: "
        + ", ".join(sorted(expected_execution_roles))
    )
for counterexample in ["团队第四执行岗位：制片人", "新增导演岗位"]:
    if not disallowed_explicit_role_declarations(counterexample):
        errors.append(f"team role declaration helper missed counterexample: {counterexample}")
if disallowed_explicit_role_declarations("剧情中的制片人走进房间，导演角色抬头看他。"):
    errors.append("team role declaration helper must ignore ordinary story occupations")
require_text(
    "router",
    router,
    [
        "资产提示词/00_资产输出总契约.md",
        "03_团队可分发提示词模板-执行版.md",
        "04_团队故事板规则.md",
        "05_编剧逻辑补充规则.md",
        "资产提示词/01A_群像单张模板.md",
        "07_讲戏表与分镜头表执行契约.md",
        "每项正式交付固定由三个岗位复核",
        "不适用时写“不涉及”及理由",
    ],
)
require_text(
    "asset compatibility router",
    asset_router,
    [
        "资产提示词/00_资产输出总契约.md",
        "不包含任何资产成稿模板",
        "资产提示词/01A_群像单张模板.md",
        "群像只使用单张 16:9",
    ],
)
require_text(
    "trigger guide",
    trigger_guide,
    [
        "群像资产",
        "资产提示词/01A_群像单张模板.md",
        "群像绝不使用 9 视图",
        "讲戏表或分镜头表",
        "逐项要求执行台账",
        "只做单镜头分镜图",
        "已有确认分镜图，只做单镜头视频",
        "一镜一图一视频",
    ],
)
require_text(
    "user guide",
    user_guide,
    [
        "只有剧本 + 明确要求补充逻辑",
        "只有剧本 + 要求拆资产",
        "剧本 + 已有分镜 + 已有资产表",
        "纯文本",
        "给了上一段尾帧，要求下一段锁定首帧",
        "给了上一段尾帧，但不要求锁定首帧",
        "### 4.2 群像资产",
        "群像绝不使用 9 视图",
        "用户是唯一对话称呼",
        "讲戏表或分镜头表",
    ],
)
require_text(
    "video framework",
    video,
    [
        "单条可复制视频提示词 `text` 正文不得超过 10000 个字符",
        "目标控制在 9500 个字符以内",
        "每个镜头都必须按以下顺序写全",
        "全局成像系统编号",
        "仅作为画外成像元数据",
        "成像系统编号【如 CAM-A】",
        "等效视角【具体焦段及透视表现】",
        "光圈【具体T值】",
        "ISO/EI、白平衡、滤镜与曝光策略",
        "运动质感与实现方式",
        "摄影、灯光、收音设备及剧组人员默认位于画外",
        "镜面、玻璃、金属反射、阴影或背景",
        "主光来源和动机",
        "主光强度",
        "主补光比",
        "轮廓光方向",
        "眼神光来源",
        "阴影方向和软硬",
        "不得写“沿用全局摄影”",
        "紧凑逐镜完整",
        "一个主要可见任务、至多一个必要反应、至多一个复杂道具操作",
        "有效时间窗、继续继承项、停止继承项和只参考项",
        "道具初始状态 -> 手从哪里接近",
        "没有触发点时不自动增加点头",
        "轴线镜像",
        "过期参考",
        "Seedance 2.0",
        "4-15 秒",
        "混合输入总上限 12 个文件",
        "Seedance 2.5",
        "最长 30 秒",
        "图片最多 30 张",
        "视频最多 10 段",
        "音频最多 10 段",
        "30 秒是硬上限，不是默认值",
        "稳定性软预算",
        "每个图片、视频、音频、白模或绿幕参考",
        "已有视频延长",
        "已有视频定向编辑",
        "白模/绿幕/视角或运镜编辑",
        "白模图接戏方式",
        "白膜图方式",
        "上一段视频抽取的清晰帧",
        "白模位置映射台账",
        "第 0 秒已经是正式人物、服装和场景",
        "0-1 秒",
        "1 秒后切入",
        "不继承白色材质",
        "Seedance 2.0 按普通空间/构图参考图兼容执行",
        "开场约 1 秒",
        "强制作为可见首帧",
        "白模图转换提示词",
        "未提供白模图时",
        "不得假定已经上传",
        "确认白模图后再生成正式视频提示词",
        "统一哑光中性白",
        "触发源 -> 发射位置与形状",
        "模型内生成还是后期完成",
        "单镜头模式不得使用切镜式转场",
        "新的生成时长只计算新增部分",
        "锁定项与可编辑项",
    ],
)
require_text(
    "white model image continuation trigger",
    skill + trigger_guide + user_guide,
    [
        "白模图接戏方式",
        "白膜图方式",
        "从上一段视频抽取一帧转成白模图",
        "第0秒已经是正式人物、服装和场景",
        "静止1秒",
        "1秒后切入后续镜头",
    ],
)
forbid_text(
    "white model visible equipment wording",
    video,
    ["人物、道具、摄影机和环境保持"],
)

expected_body_headings = [
    "【素材与指代映射】",
    "【一句话片段概述】",
    "【全局成像与灯光基准】",
    "【连续时间线/逐镜正文】",
    "【声音】",
    "【结尾与尾帧】",
    "【必要限制项】",
]
production_card = text_block_after(
    "team video production card",
    video,
    "### 1. 内部生产卡附表",
)
if "白模图接戏卡" in production_card:
    errors.append("team base production card must omit the conditional white-model card")
model_body = text_block_after(
    "team video model body",
    video,
    "### 2. 可复制模型正文",
)
actual_body_headings = re.findall(r"^【[^】]+】$", model_body, re.MULTILINE)
if actual_body_headings != expected_body_headings:
    errors.append(
        "team video model body headings must be exactly seven in fixed order: "
        + " -> ".join(expected_body_headings)
    )
for heading in expected_body_headings:
    if model_body.count(heading) != 1:
        errors.append(f"team video model body heading must appear once: {heading}")
if "【本段任务】" in model_body:
    errors.append("team video model body must not contain: 【本段任务】")
for bad_line in ["模型路由：Seedance 2.5", "内部审查：已通过"]:
    counterexample_body = model_body + "\n" + bad_line
    if not production_card_lines_in_model_body(counterexample_body):
        errors.append(f"team video body helper missed counterexample: {bad_line}")
forbidden_body_lines = production_card_lines_in_model_body(model_body)
if forbidden_body_lines:
    errors.append(
        "team video model body contains production-card-only lines: "
        + " | ".join(forbidden_body_lines)
    )

legacy_markdown_headings = re.findall(
    r"^#{2,6}\s+(【[^】]+】)\s*$",
    video,
    re.MULTILINE,
)
if legacy_markdown_headings:
    errors.append(
        "team video legacy bracket headings remain outside canonical blocks: "
        + ", ".join(legacy_markdown_headings)
    )
if "可复制模型正文在前，内部生产卡附表在后" not in video:
    errors.append("team video delivery order must put model body before production card")

production_card_fields = [
    "模型路由：",
    "类型、画幅、节奏与影调：",
    "讲戏表/分镜头表执行台账：",
    "生产方式：",
    "资产调用台账：",
    "参考输入与权重：",
    "空间与站位：",
    "【本段任务】",
    "节奏：",
    "素材：",
    "连续性：",
    "表演调度：",
    "摄影：",
    "灯光：",
    "声音：",
    "特效/转场：",
    "尾帧：",
    "内部审查：",
]
require_text("team video production card fields", production_card, production_card_fields)
video_without_card = video.replace(production_card, "", 1)
if "【本段任务】" in video_without_card:
    errors.append("team video 【本段任务】 must appear only inside production card")
if "【全局画质与连续性】" in video:
    errors.append("team video must merge global quality and continuity into seven-section body")

team_entry_text = "\n".join([skill, trigger_guide, user_guide])
forbid_text(
    "team entry legacy video routing",
    team_entry_text,
    [
        "【全局摄影与灯光规则】",
        "先写模型路由卡",
        "填写模型路由卡",
        "写入模型路由卡",
        "只改变模型路由卡",
    ],
)
require_text(
    "team SKILL seven-section routing",
    skill,
    [
        "【全局成像与灯光基准】",
        "模型路由、类型节奏、讲戏/分镜台账、生产方式、资产台账、空间站位、本段任务只写内部生产卡",
        "正文仍只输出七段",
    ],
)
for entry_label, entry_text in [
    ("team user guide", user_guide),
    ("team trigger guide", trigger_guide),
]:
    require_text(
        f"{entry_label} seven-section routing",
        entry_text,
        ["先在内部生产卡填写", "正文仍只输出七段"],
    )
require_text(
    "team video dual-delivery framework",
    video,
    [
        "内部生产卡附表",
        "可复制模型正文",
        "正式交付缺少任一块均不通过",
        "先完成内部生产卡，再据此写可复制模型正文",
        "可复制模型正文在前，内部生产卡附表在后",
        "【素材与指代映射】",
        "【一句话片段概述】",
        "【全局成像与灯光基准】",
        "【连续时间线/逐镜正文】",
        "【结尾与尾帧】",
        "【必要限制项】",
        "总计最多 50 个参考素材",
        "图片建议不高于 4K",
        "视频最多 10 段且总长不超过 30 秒",
        "音频最多 10 段且总长不超过 30 秒",
        "Seedance 2.5 使用连续整数秒时间段",
        "Seedance 2.0 不冒用 2.5 的精准时间线",
        "按当前入口允许次数执行延长",
        "前状态 -> 转换触发 -> 物理/图形变化 -> 后状态 -> 连续元素",
    ],
)
require_text(
    "team video asset invocation contract",
    video,
    [
        "资产调用：@完整资产名_Vn",
        "映射表与逐镜资产调用必须双向一致",
        "正文实际出现的人物、场景、关键道具和特效",
    ],
)
require_text(
    "team video per-shot camera body exclusion",
    video,
    [
        "逐镜不得出现摄影机品牌、摄影机型号或机身名称",
        "摄影机型号只允许在【全局成像与灯光基准】出现一次",
    ],
)
require_text(
    "team Seedance 2.5 opt-in reference gate",
    video + skill + user_guide,
    [
        "只指定 Seedance 2.5 不等于启用白模或参考视频",
        "默认纯文本资产分支",
        "不得输出白模位置映射、白模转换提示词、参考视频运动轨迹",
    ],
)
shot_template = text_block_after(
    "team video shot template",
    video,
    "每个镜头都必须按以下顺序写全",
)
if "资产调用：@完整资产名_Vn" not in shot_template:
    errors.append("team video shot template missing complete @asset invocation field")
for forbidden in ["摄影机型号", "机身型号", "ARRI ", "RED ", "Sony VENICE"]:
    if forbidden in shot_template:
        errors.append(f"team video shot template contains camera body metadata: {forbidden}")
forbid_text(
    "team video obsolete Seedance wording",
    video + user_guide,
    ["0.5 秒粒度", "支持两次视频延长"],
)
require_text(
    "seedance route trigger",
    skill + user_guide,
    [
        "用 Seedance 2.0",
        "用 Seedance 2.5",
        "未指定 Seedance 2.0 或 Seedance 2.5 时",
        "先询问用户",
        "共用同一套视频提示词骨架",
    ],
)
require_text(
    "team manual seedance route comparison",
    user_guide,
    [
        "模型路由口令，必须二选一",
        "本次用 Seedance 2.0，请先在内部生产卡填写2.0路由",
        "本次用 Seedance 2.5，请先在内部生产卡填写2.5路由",
        "4-15秒",
        "混合输入总上限12个文件",
        "最长30秒",
        "最多30张",
        "最多10段",
        "时间戳定向编辑、白模、绿幕、视角或运镜编辑按当前入口实际开放情况启用",
        "不能原样输入“Seedance 2.0/2.5”",
        "已有视频延长，仅Seedance 2.5",
        "已有视频定向编辑，仅Seedance 2.5",
    ],
)
forbid_text(
    "team manual unresolved model placeholder",
    user_guide,
    ["本次用 Seedance 2.0/2.5"],
)
forbid_text(
    "video framework",
    video,
    [
        "独立服装资产四宫格模板",
        "资产生图固定规格",
        "人物 9 视图",
        "人物9视图",
        "群像人物资产单张模板",
        "摄影机型号【具体型号】",
        "摄影机型号可以为保持项目一致而相同，但必须逐镜写出",
    ],
)
require_text(
    "storyboard",
    storyboard,
    [
        "单个故事板最多 4 格",
        "黑白线稿",
        "故事板提示词模板",
        "讲戏表/分镜头表执行台账",
    ],
)
forbid_text(
    "storyboard",
    storyboard,
    ["通用 AI 视频顺序提示词模板", "视频提示词总模板"],
)

markdown = "\n".join(path.read_text(encoding="utf-8") for path in ROOT.rglob("*.md"))
package_text = "\n".join(
    path.read_text(encoding="utf-8")
    for path in ROOT.rglob("*")
    if path.is_file() and path.suffix.lower() in {".md", ".yaml", ".yml"}
)
forbid_text(
    "package unresolved model placeholder",
    markdown,
    ["本次用 Seedance 2.0/2.5"],
)
forbid_text(
    "seedance fixed-duration leftovers",
    markdown,
    ["默认按15秒生成单元", "默认15秒生成单元", "固定15秒生成单元"],
)
forbid_text(
    "package",
    markdown,
    [
        "独立服装资产四宫格模板",
        "核心场景不得只给单张图",
        "1-3镜",
        "3-5镜",
        "4-6镜",
        "视频提示词第0节模板",
        "视频模板第0节",
        "通用 AI 视频顺序提示词模板",
        "视频提示词总模板",
        "群体中的可识别人物逐人建立人物资产",
        "不建立群像合影版式",
        "四类唯一资产模板",
        "四类唯一模板",
        "仅有的四种正式版式",
    ],
)

require_text(
    "asset contract",
    assets,
    [
        "@1-1林小满日常装_V1",
        "方案版本",
        "确认状态",
        "替代/来源版本",
        "当前有效版本",
        "候选 / 已确认 / 已淘汰",
        "只有已确认版本",
        "新剧情状态",
        "从自己的 `V1` 开始",
        "仅复用已确认资产时不增加版本",
        "人物 9 视图",
        "群像单张",
        "场景单张五面空间",
        "道具四宫格",
        "特效四宫格",
        "资产类型\\t资产名称\\t资产用途\\t优先级\\t提示词",
        "同一物理场景只建立一个空间母版",
        "人物第一次正式出现的完整形象就是首态母版",
        "不得另做裸体",
        "基于@原场景空间母版",
        "时段/天气派生状态",
        "P0根母版",
        "P1独立核心",
        "P2关联派生",
        "P3次要补充",
        "人物专属道具",
        "操作状态链",
        "换装节点台账",
        "仅日夜或情绪变化不能自动触发换装",
        "换回旧装直接复用旧资产",
    ],
)

execution_contract = read("references/团队故事板规则包/07_讲戏表与分镜头表执行契约.md")
require_text(
    "lecture and shot-list execution contract",
    execution_contract,
    [
        "讲戏表或分镜头表是后续执行的强制输入",
        "逐项要求执行台账",
        "资产、故事板、视频提示词",
        "不得擅自改写、删减、重排或用默认模板覆盖",
        "冲突项保留原要求并标记待用户确认",
    ],
)

forbid_text(
    "team address leaks",
    markdown,
    [
        "待导演确认",
        "仍需导演判断",
        "需要导演确认",
        "导演要求和导演判断",
        "测试导演",
        "导演您好",
    ],
)

group = read("references/团队故事板规则包/资产提示词/01A_群像单张模板.md")
require_text(
    "group template",
    group,
    [
        "单张 16:9 横屏群像人物定妆资产图",
        "群像不使用 9 视图",
        "固定【人数】名",
        "从头到脚完整可见",
        "纯中性浅灰",
        "Hasselblad X2D 100C",
        "光圈 f/8",
        "主补光比约 2:1",
        "逐人描述",
    ],
)

person = read("references/团队故事板规则包/资产提示词/01_人物9视图模板.md")
require_text(
    "person template",
    person,
    ["首次人物首态母版", "不得生成裸体", "换装节点", "换装必要性", "来源人物首态母版", "换回节点/后续复用"],
)
require_text(
    "team person conditional body proportion card",
    person,
    [
        "条件式身体比例卡",
        "头身单位定义为头顶至下巴",
        "头身比",
        "肩线、肋骨箱、腰线与骨盆",
        "裆点",
        "膝点",
        "手脚尺度",
        "肌肉与脂肪分布",
        "已确认母版优先",
        "未成年角色",
        "腰臀比是腰围除以臀围",
        "不得把未定义的腿长百分比",
    ],
)
forbid_text(
    "team person unsafe fixed body ratios",
    person,
    ["肩腰比0.6", "腿长60%", "腿长55%", "腰臀比0.75", "超模质感直接拉满"],
)
require_text(
    "team asset contract conditional body proportion routing",
    assets,
    ["条件式身体比例卡", "已有已确认人物母版时不得重新计算比例"],
)

scene = read("references/团队故事板规则包/资产提示词/02_场景单张五面空间模板.md")
require_text(
    "scene template",
    scene,
    ["时段/天气派生状态", "基于@【原场景空间母版】"],
)

mj_root = "references/团队故事板规则包/资产提示词/Midjourney V7"
mj_contract = read(f"{mj_root}/00_Midjourney V7资产路由与总契约.md")
mj_person = read(f"{mj_root}/01_人物9视图模板.md")
mj_group = read(f"{mj_root}/01A_群像单张模板.md")
mj_scene = read(f"{mj_root}/02_场景单张五面空间模板.md")
mj_prop = read(f"{mj_root}/03_道具四宫格模板.md")
mj_effect = read(f"{mj_root}/04_特效四宫格模板.md")
mj_markdown = "\n".join(
    [mj_contract, mj_person, mj_group, mj_scene, mj_prop, mj_effect]
)

image_rules_match = re.search(
    r"^## 生图与画质总规则\s*$\r?\n(.*?)(?=^##\s)",
    assets,
    re.MULTILINE | re.DOTALL,
)
if not image_rules_match:
    errors.append("asset contract missing image model routing section")
else:
    image_rules = image_rules_match.group(1)
    gpt_heading = "### GPT Image 2 路由"
    mj_heading = "### Midjourney V7 路由"
    require_text(
        "asset contract strict image model branches",
        image_rules,
        [gpt_heading, mj_heading],
    )
    if gpt_heading in image_rules and mj_heading in image_rules:
        universal_rules, model_rules = image_rules.split(gpt_heading, 1)
        gpt_rules, mj_rules = model_rules.split(mj_heading, 1)
        forbid_text(
            "asset contract universal image rules",
            universal_rules,
            ["GPT Image 2", "gpt-image-2", "4K"],
        )
        require_text(
            "asset contract GPT Image 2 branch",
            gpt_rules,
            ["gpt-image-2", "4K", "平台最高质量"],
        )
        forbid_text(
            "asset contract Midjourney V7 branch",
            mj_rules,
            ["GPT Image 2", "gpt-image-2", "4K"],
        )
        require_text(
            "asset contract Midjourney V7 branch",
            mj_rules,
            ["只读", "Midjourney V7资产路由与总契约.md", "对应的一种 V7 类型模板"],
        )

require_text(
    "team Midjourney V7 route contract",
    assets + skill + user_guide + mj_contract,
    [
        "先选择生图模型，再选择资产类型",
        "GPT Image 2 / Midjourney V7",
        "一次只命中一套正式模板",
        "--v 7 --raw --q 2",
        "--iw",
        "--sref",
        "--sw",
        "--ow",
        "Omni Reference 一次只使用一张",
        "Subtle Upscale",
        "真实 `.xlsx`",
        "固定五列 `.tsv`",
    ],
)
require_text(
    "team Midjourney V7 person layout",
    mj_person,
    ["16:9 横屏人物 9 视图", "五列排版", "单人人物/人物状态"],
)
require_text(
    "team Midjourney V7 person conditional body proportion card",
    mj_person,
    [
        "条件式身体比例卡",
        "头身单位定义为头顶至下巴",
        "肩线、肋骨箱、腰线与骨盆",
        "裆点",
        "膝点",
        "已确认母版优先",
        "未成年角色",
    ],
)
forbid_text(
    "team Midjourney V7 person unsafe fixed body ratios",
    mj_person,
    ["肩腰比0.6", "腿长60%", "腿长55%", "腰臀比0.75", "超模质感直接拉满"],
)
require_text(
    "team Midjourney V7 group layout",
    mj_group,
    ["16:9 单张完整群像", "群像不使用 9 视图"],
)
require_text(
    "team Midjourney V7 scene layout",
    mj_scene,
    ["2.35:1 单张", "五面空间", "空场景，禁止出现人物"],
)
require_text(
    "team Midjourney V7 prop layout",
    mj_prop,
    ["16:9 横屏四宫格", "同一个道具主体"],
)
require_text(
    "team Midjourney V7 effect layout",
    mj_effect,
    ["16:9 横屏四宫格", "同一个特效主体", "光照反馈"],
)
forbid_text(
    "team Midjourney V7 obsolete or false parameters",
    mj_markdown,
    ["--style raw", "--q 0.5", "原生 4K"],
)
forbid_text(
    "team Midjourney V7 role leakage",
    mj_markdown,
    TEAM_CONTEXT_LEAK_MARKERS,
)

mj_templates = {
    "person": mj_person,
    "group": mj_group,
    "scene": mj_scene,
    "prop": mj_prop,
    "effect": mj_effect,
}
expected_base_aspect_ratios = {
    "person": "16:9",
    "group": "16:9",
    "scene": "235:100",
    "prop": "16:9",
    "effect": "16:9",
}
for template_name, template_text in mj_templates.items():
    base_prompt = first_text_block(
        f"team Midjourney V7 {template_name} base prompt",
        template_text,
    )
    aspect_ratios = re.findall(r"--ar\s+([^\s]+)", base_prompt)
    expected_ratio = expected_base_aspect_ratios[template_name]
    if aspect_ratios != [expected_ratio]:
        errors.append(
            f"team Midjourney V7 {template_name} base prompt --ar expected {expected_ratio}, got {aspect_ratios}"
        )
    for parameter in ["--iw", "--ow", "--sref", "--sw"]:
        if parameter in base_prompt:
            errors.append(
                f"team Midjourney V7 {template_name} base prompt contains unconditional reference parameter: {parameter}"
            )
    require_text(
        f"team Midjourney V7 {template_name} conditional references",
        template_text,
        [
            "无参考分支：删除所有引用参数",
            "有参考分支：",
            "普通图片URL放在提示词开头",
            "--iw",
            "【单一Omni参考URL/平台输入槽】",
            "--ow",
            "风格URL",
            "--sref",
            "--sw",
        ],
    )

require_text(
    "team Midjourney V7 fixed delivery",
    mj_contract,
    [
        "【资产拆分清单】",
        "【资产命名台账】",
        "【资产审查结论】",
        "【完整TSV资产提示词表】",
        "真实 `.xlsx`",
        "固定五列 `.tsv`",
        "资产类型\\t资产名称\\t资产用途\\t优先级\\t提示词",
    ],
)

forbid_text(
    "team full-package context leakage",
    package_text,
    TEAM_CONTEXT_LEAK_MARKERS,
)

disallowed_roles = disallowed_explicit_role_declarations(package_text)
if disallowed_roles:
    errors.append(
        "team full-package contains disallowed explicit role declarations: "
        + ", ".join(sorted(set(disallowed_roles)))
    )

yaml_size = (ROOT / "agents/openai.yaml").stat().st_size
if yaml_size > 900:
    errors.append(f"agents/openai.yaml too large: {yaml_size} bytes")

package_file_count = sum(
    1 for path in ROOT.rglob("*") if path.is_file() and ".git" not in path.parts
)

if errors:
    print("TEAM CONTRACT VALIDATION FAILED")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print(
    "TEAM CONTRACT VALIDATION PASSED "
    f"files={package_file_count} "
    f"markdown={sum(1 for p in ROOT.rglob('*.md'))} "
    f"openai_yaml_bytes={yaml_size}"
)
