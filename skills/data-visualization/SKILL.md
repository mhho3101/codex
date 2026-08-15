---
name: data-visualization
description: 数据可视化——用 Python(matplotlib/plotly)、HTML 图表把数据变成清晰的可视化图形，可导出为视频画面所需的图表素材。需要制作图表、信息图、数据动画时使用本技能。
---

# 数据可视化技能

把数据转化为清晰、美观、适合展示（含视频画面）的可视化。先确认数据与目标，再选工具。

## 选择工具

| 场景 | 工具 |
|---|---|
| 静态统计图（折线/柱状/饼图） | matplotlib |
| 交互式图表 / 网页嵌入 | plotly |
| 大屏 / 信息图 | HTML + ECharts |
| 数据动画（视频用） | matplotlib.animation / manim |
| 快速探索数据 | pandas + seaborn |

## matplotlib 要点

```python
import matplotlib.pyplot as plt
import matplotlib
# 中文字体（Windows）
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
matplotlib.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
ax.plot(x, y, color="#2E86DE", linewidth=2.5)
ax.set_title("标题", fontsize=16, pad=12)
ax.set_xlabel("X 轴"); ax.set_ylabel("Y 轴")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("chart.png", dpi=150)   # 高清导出，适合视频
```

## 图表规范

- **配色**：用统一色板（如 2E86DE / F39C12 / E74C3C / 27AE60），一次不超过 5 色
- **字体**：中文用微软雅黑，标题 ≥16pt，正文 ≥12pt
- **尺寸**：视频画面建议 16:9（1920×1080）或 9:16（1080×1920），`figsize` 按比例设置，`dpi=150` 以上
- **去噪**：去掉默认边框（`ax.spines`）、过密网格、多余小数
- **数据标签**：柱状/饼图直接标数值，避免读者对照坐标轴
- **对比度**：深色背景视频用浅色线条 + 高对比色，检查文字可读性

## 数据动画（视频素材）

```python
import matplotlib.animation as animation
from IPython.display import HTML

fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
line, = ax.plot([], [], lw=2)

def update(i):
    line.set_data(x[:i], y[:i])
    ax.set_xlim(0, len(x)); ax.set_ylim(y.min(), y.max())
    return line,

anim = animation.FuncAnimation(fig, update, frames=len(x), interval=50)
anim.save("animation.mp4", writer="ffmpeg", fps=20)  # 直接导出视频
```

## plotly 要点

```python
import plotly.express as px
fig = px.line(df, x="日期", y="数值", color="类别", title="趋势")
fig.update_layout(template="plotly_white", font=dict(family="Microsoft YaHei"))
fig.write_html("chart.html")        # 交互式
fig.write_image("chart.png")        # 需安装 kaleido
```

## ECharts（HTML 大屏/信息图）

- 单个 HTML 文件引入 `https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js`
- `title`、`tooltip`、`legend` 全中文配置
- 深色主题：`{ backgroundColor: '#0f1115' }` + 亮色 series

## 交付检查清单

- [ ] 图表传达的核心信息一眼可读
- [ ] 中文无乱码（字体已配置）
- [ ] 分辨率满足用途（视频 ≥150dpi 或直接导出 mp4）
- [ ] 颜色对比达标（黑白下仍可辨认）
- [ ] 数据准确，无截断误导（Y 轴不从非零处随意截断）
