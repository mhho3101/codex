# Changelog

本项目遵循语义化版本。格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [v3.4.0] - 2026-09-08

真实客户实战修复（8-25 全流程梳理暴露：通用机判阈值与成片实测严重冲突，实战被迫改人工判）。

### Added
- **`check --client <cid>` 客户化校准**：读取 `clients/<cid>/06-standard.md` 的「机判校准」机器可读区（max_sentence_len / action_words / good_openers / good_closers），替代通用 15 字/通用词表；无校准区时回退通用规则。
- standard-card 模板新增「机判校准」空占位区（留空=通用规则；按成片实测 P90 与词频填写）。

### Fixed
- 客户专属标准卡从"给人看的档案"变为"check 命令读取的配置"——标准挖掘→客户校准→机判的链路接通。
- 实测验证：B2B 服务口播真实稿（成片句长中位 25 字、P90≈54 字）通用规则拦 7 句长句 → 客户化校准后仅拦 2 句真正超 P90 的句子。

## [v3.3.0] - 2026-08-21

全环节机判化升级（P0+P1+P2 提升清单全部落地）。

### Added
- **`aha`**：自动算近 10 条播放基准线，标超基线条目（≥1.5x），输出 A/B/C 判级建议与拍穿种子。
- **`patrol`**：每日巡检——挂起超期（≥15 天转待决策）/buffer 红灯/待复盘（预测超 3 天未复盘）/待回标，一扫全部客户。
- **`schedule`**：排期纪律机判——3 连窗口全对立冲突钩子告警、信任实证类占比 <40% 报出。
- **`seed`**：冷启动搜索任务清单生成（关键词×痛点词×人群，带筛选规则）。
- **`archive`**：客户归档到 clients/_archive，registry 标记。
- **`check` 第四段合规扫描**：绝对化/违禁词机判（月入过万/必治/必然转运/全网第一等，区分「第一」排序声称与过渡词防误报）。
- **`metrics` 预测精度**：盲预测 vs 实际播放的偏差趋势（支持 万/w 写法）。
- **`adapters/README.md`**：对标成对样本/回标/热点候选的输入契约（任何取数工具可接）。
- **`templates/discovery-questionnaire.md`**：商业诊断七问问卷（采访前发客户）。

### Changed
- **`status` 打通状态机**：作战台读 05-state.md（六态+buffer+挂起），按 buffer/挂起紧急度排序，保留 v1 缺口推断为辅助。
- planning.md A1 接入诊断问卷；A6 自查清单加定位验证清单项。

## [v3.2.0] - 2026-08-21

### Added
- **定位模式库**（`references/positioning-patterns.md`）：模块 A 从"只靠内部方法论"升级为"有对标依据+网络复现经验"——定位四维/定位公式/人设四要素+放大法/差异化两路径/客群拆解法/起号三目标/场景三传递/变现路径先定 + 定位验证清单；证据分级标注（★内部已验证 / ☆公开方法论）。

### Changed
- SKILL.md 模块 A、planning.md A2.5 接入定位模式库；定稿前过验证清单。

## [v3.1.1] - 2026-08-21

### Added
- copy-patterns.md 并入本地 PATTERNS 生长库的通用精华：五段式长口播、三大内容线、正文展开 16 模型、收尾公式、CTA 承接模型、合规红线（通用化）；说教版 vs 爆款版完整案例对比。

### Changed
- **合并治理**：copy-patterns.md 与 script-structure.md 确立为文案方法论单一正本；工具箱 video-copywriting 技能改为薄壳路由（本地生长库 PATTERNS.md 保留行业专属模型与溯源，永不进公开包）。
- script-structure.md 逻辑关补三关系检查法内联示例（移除对工具箱内部技能的外部引用）。

## [v3.1.0] - 2026-08-21

融入 video-copywriting 爆款文案方法论到模块 C（脚本生产）。

### Added
- **文案模式库**（`references/copy-patterns.md`）：八大爆款公式 / 黄金结构 / 钩子句式库 / 金句压缩 / 过渡技巧 / 共鸣写法六要点（全部去客户化）。
- **`check` 命令**：文案三关校验——格式关（句长≤15字含短句连击豁免/书面禁用词/人称）与结构关（开头词表/动作词表/行动锚点收尾）确定性机判，逻辑关输出编号句供三关系检查。
- 脚本起草"步骤 0 查阅模式库"（references/script-structure.md）。

### Changed
- 四关校验 v2：格式关/结构关细化为可机判规则；逻辑关升级为三关系检查法；钩子关新增攻击性/冲击力自检；常见错误清单补共鸣/画面感/过渡三项。
- 脚本卡模板四关校验区更新为 v2 细则。

## [v3.0.1] - 2026-08-21

### Fixed
- **bug**：新客户 predictions/ 目录不存在时，`shoot` 的条件短路导致未写盲预测也能登记拍摄（实测复现）→ 重写判定逻辑，未 predict 一律拒绝。
- README 首屏金句改写为原创表述（原句与对标仓库文案过于接近）。

### Changed
- README 快速开始补全 v3 动作（predict/shoot/publish/retro/bump/recommend/state）。
- English Layout 补 v3 新卡与新命令清单；walkthrough 新增 v3 盲预测→拍发分离→复盘演示段。

## [v3.0.0] - 2026-08-21

对标 XBuilderLAB/cheat-on-content 做颗粒度对齐：动作粒度对齐，物理结构保持单包轻量。

### Added
- **盲预测 immutable**：`predict` 发布前建档，`## 预测` 段写完不可改；重做只能新开 `_redo.md`；Claude Code 可选 hook（`hooks/prediction-immutability.sh`）物理拦截直接编辑。
- **拍/发分离**：`shoot`（buffer +1）/ `publish`（buffer -1）；buffer 绿黄红三档警戒，红灯（≥3）停止新拍摄先发布。
- **retro 只追加**：`retro` 只往 `## 复盘` 段追加，不动预测段。
- **标准卡 bump 协议**（`references/bump-protocol.md`）：全量重打校准池 + 排序一致性 ≥4/5 + 独立审核，不达标拒升；观察生命周期规则（被推翻/被吸收即删）。
- **隔离盲评协议**（`references/score-blind.md`）：评分上下文不得混入实际数据；按 harness 能力三档执行。
- **buffer 感知推荐**：`recommend` 按节奏给"1 稳 + 1 实验"，红灯只催发布；候选池读取「状态：候选」选题与 trends 格式待评行。
- **受众画像**：`persona` 从回标评论聚类派生骨架（盲评上下文禁读）。
- **热点候选池约定**（`references/trends-and-candidates.md`）。
- **Refusals 清单**：SKILL.md 新增"必须拒绝的请求"段 + 各 references 卡内详细场景。
- **migrate**：老客户目录补齐 05-state/06-standard 并打 schema 版本标（当前 schema v3）。

### Changed
- 目录约定五件套 → 七件套 + predictions/ 目录 + audience.md。
- 运行状态模板新增 schema/buffer 字段；标准卡模板新增生命周期与 bump 记录区。

## [v2.1.0] - 2026-08-21

### Fixed
- **可移植性**：老 Windows cmd（GBK 控制台）运行 director.py 不再崩溃（输出加 errors=replace 防护，emoji 自动降级为 `?`）。
- 实测 Python 3.11 / 3.12 / 3.14 全通过；整个包拷贝到任意干净目录可跑（零绝对路径）。

### Changed
- README 新增环境要求表（Agent 层/引擎层/控制台/网络/LLM 五层）。

## [v2.0.0] - 2026-08-21

### Added
- **常驻循环**：每客户六态状态机（待定位确认→冷启动选题→脚本生产→待拍摄发布→回标评估→拍穿放大），事件驱动唤醒，挂起写代办不空转（`references/persistent-loop.md`）。
- **标准挖掘**：对标样本"爆款 vs 普通"成对对照 → 客户专属评分权重，叠加通用 8 项闸门（`references/standard-mining.md`）。
- **定位五步**（planning.md A2.5）：锁客户→商业诊断→目标审计→采访挖素材→合成定位卡；客户确认前不出题。
- **缺口清单**：脚本起草前必填"必须说清的事：有原话/空的"（`templates/gap-checklist.md`）。
- **Aha 判级**：回标对照账号基准线判 A/B/C 级，A 级进拍穿计划（data-loop.md）。
- **新命令**：`director.py state <cid>` 查看/更新客户运行状态。
- **新模板** ×4：positioning-card / standard-card / gap-checklist / running-state。
- 客户目录五件套升级为七件套（+05-state.md 运行状态、+06-standard.md 标准卡）。

### Fixed
- 脱敏：虚构示例客户行业修正（原用词与真实客户行业重叠，软性泄露点）；扩展关键词扫描 0 命中。

## [v1.0.0] - 2026-08-17

### Added
- 首次发布：策划诊断 → 选题生成（连连看矩阵+钩子库 23 类+8 项评分闸门）→ 脚本生产（四关校验）→ 发布排期与承接 → 数据回标 → 复利沉淀。
- 引擎 `scripts/director.py`：onboard / status / matrix / assemble / score / metrics，纯标准库离线可跑，`--llm` 可选增强。
- 五条红线、行业迁移卡、demo 客户 walkthrough。
