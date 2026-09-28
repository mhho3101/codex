# 故障排查参考

> 出错时按需查阅。所有命令都是 `python scripts/api_client.py <子命令>`。

## 配置与鉴权

| 问题 | 排查方向 |
|------|---------|
| `check-config` 返回 missing | 走 Stage 0 索要火山 ARK key |
| `save-key` 报"必须以 ark- 开头" | 粘的不是火山 ARK key。去 https://console.volcengine.com/ark API Key 管理里复制 `ark-` 开头的那串 |
| ARK key 无效 / 鉴权失败 | key 不完整、被吊销或账户欠费。重新 save-key,或去控制台重建 key |
| 偏好/预检记录乱了 | `save-prefs --clear` 清空偏好;换 key 时预检记录会自动清空 |

## 渠道预检

| 问题 | 排查方向 |
|------|---------|
| `check-video-channel` 返回 `model_not_open` | **不是 skill bug**。登录 https://console.volcengine.com/ark/region:ark+cn-beijing/model,在「模型管理」里找到对应模型点「开通」(免费) |
| `check-image-channel` 默认探测结果存疑 | 默认是零成本探测(靠参数报错推断渠道通);要 100% 确证加 `--real`(约 $0.02,顺带验证默认尺寸) |
| 预检 `status: unknown`(网络错误) | 网络抖动,可以直接跑真实生成测试 |
| 换了 `--model` 后预检结果还是旧的 | 预检按"类型:模型 ID"分别记录,对新模型重跑一次对应 check-*-channel |

## 生图(Seedream)

| 问题 | 排查方向 |
|------|---------|
| 生图失败 `model not / 未开通` | 图片模型未开通,同上去控制台点开通 |
| 生图失败 "size invalid" | 命令会自动回退到比例式 `9:16` 重试(stderr 有提示)。如果回退也失败,手动试 `--size 1024x1820` 或查该模型支持的尺寸枚举 |
| **画幅注意** | 真 9:16 是 `1080x1920`;**`1024x1536` 是 2:3 不是 9:16**,会被视频环节裁切或拉伸,别用 |
| 图生图编辑后主体跑偏 | edit prompt 太宽泛。按"改/承/锁"三段式收紧,明确"只改这一处";或重新生成基准图 |
| 编辑后状态跳跃过大 | edit prompt 缺"承接推进"段——只写了"换 A 为 B",没写"保留并自然推进 XX 状态"。回 Stage 3 补 |
| 视觉自检连续 2 次不过 | 别再盲目重试,带着图和具体问题找用户对齐(可能是锚定方案本身有问题) |

## 生视频与配音(Seedance)

| 问题 | 排查方向 |
|------|---------|
| 创建任务 401/403 | key 问题,回 Stage 0 |
| 创建任务 403 / 余额不足 | 去 https://console.volcengine.com/ark 充值 |
| 创建任务 404 / model_not_found | 模型 ID 拼写错。默认 `doubao-seedance-1-5-pro-251215`;备选 `doubao-seedance-1-0-pro-250528` / `doubao-seedance-1-0-pro-fast-251015`(1.0 系列无音频但便宜) |
| 图片格式问题 | Seedance 要求 JPEG/PNG/WebP、≤10MB、最小边长约 300px |
| 任务一直 queued/running | 正常排队,脚本每 10 秒查一次,超 10 分钟才算超时 |
| 任务 failed | 看 `error` 字段。常见:内容审核(人脸/品牌/敏感词)、图片不合规。换图或调 prompt 重试 |
| **batch 里个别镜失败** | 其他镜不受影响。看汇总 JSON 里失败项的 error,单独用 `gen-video-clip` 重做那一镜 |
| **任务"消失"无文件无报错** | 90% 是把生成命令放后台跑(`run_in_background`)且 API 报错被吞。**改前台运行**,stderr 会逐 status 打印进度 |
| 视频画幅不对(横屏) | 检查 jobs/参数里 `aspect_ratio` 是否 9:16(脚本默认会加 `--ratio 9:16`) |
| 动作不对/主体变形 | Seedance 有随机性,重新生成该镜;连续 2 次不对就把 motion prompt 的物理细节写更具体,或重出基准图 |
| 没有配音/不是预期声线 | 检查该镜 `voiceover_text` 非空;音色细节见 `references/voice-presets.md` |
| 配音被画面截断 | 台词太长。压到 8-12 字,或单镜 `duration` 改 10(注意总时长变化) |
| 配音读错字 | 偶发,重生成该镜;或剪映里关原音轨用"文本朗读"替代 |
| 想换模型 | `--model` 覆盖(单镜和 batch 都支持)。换 1.0 系列后**音频失效**;成本估算记得带上 `estimate-cost --video-model <新模型>` |

## 拼接与抽帧(ffmpeg)

| 问题 | 排查方向 |
|------|---------|
| "ffmpeg 不在系统 PATH 里" | macOS `brew install ffmpeg`;Ubuntu `sudo apt install ffmpeg`;Windows 去 https://www.gyan.dev/ffmpeg/builds/ 下载加 PATH。不装也不阻断——3 段 mp4 拖进剪映手动拼 |
| 拼接报 "Non monotonous DTS" | stream copy 模式偶发,脚本会自动 fallback 到 H.264 重编码(慢但稳)。fallback 也失败就检查 3 段 mp4 参数是否一致 |
| 成片接缝处跳帧/黑屏 | 接缝视觉不连续——回 Stage 2 检查"状态承接"设计,或重生成有问题的那一镜 |
| `extract-frames` 抽不出尾帧 | 脚本会自动从 -0.3s 回退到 -1.0s 重试;还失败说明视频文件损坏,重新下载/生成 |

## 流程级

| 问题 | 排查方向 |
|------|---------|
| 想"只重做第 2 镜" | 重生成该镜图(如需)→ `gen-video-clip` 重做该镜视频 → 重跑 `concat-clips`。其他镜不动,project.json 里更新对应文件记录 |
| 想继续上次中断的项目 | 找最新的 `output/*/project.json`,读 `stage` 字段从那里接着走,已确认的锚定/分镜不再重新对齐 |
| 提案选题总是老几样 | 环境可能不支持 web 检索(agent 应已声明)。让用户贴自己刷到的爆款链接/截图,这比盲搜更准 |
| 做第二条视频覆盖了第一条 | 不应发生——每条视频都要先 `init-project` 建独立目录。如果发生了说明跳过了这一步 |
