---
name: ffmpeg-video-processing
description: ffmpeg 视频处理命令专项——裁剪、拼接、转码、压缩、字幕烧录、音频处理、变速、抽帧与批量处理。处理音视频文件时使用本技能。
---

# ffmpeg 视频处理命令手册

处理音视频优先用 ffmpeg。先确认 ffmpeg 可用（`ffmpeg -version`），未安装时先安装：
- Windows: `winget install ffmpeg` 或 `choco install ffmpeg`
- 检查多音频/视频流：`ffprobe input.mp4`

## 基础

```bash
# 查看媒体信息
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4

# 转码（H.264 + AAC，高质量）
ffmpeg -i input.mp4 -c:v libx264 -crf 20 -preset medium -c:a aac out.mp4

# 压缩（CRF 越高越小，18~28）
ffmpeg -i input.mp4 -c:v libx264 -crf 28 -preset medium -c:a aac out_small.mp4
```

## 裁剪与拼接

```bash
# 时间裁剪（保留 00:00:10 到 00:01:30）
ffmpeg -ss 00:00:10 -to 00:01:30 -i input.mp4 -c copy cut.mp4

# 无损拼接（同参数素材，用 concat demuxer）
# 先建 list.txt：file 'part1.mp4' 每行一个
ffmpeg -f concat -safe 0 -i list.txt -c copy merged.mp4

# 精确裁剪并重编码（剪切点精确）
ffmpeg -i input.mp4 -ss 10 -t 80 -c:v libx264 -crf 20 -c:a aac out.mp4
```

## 转场（xfade）

```bash
# 两段视频交叉淡化 1 秒（先统一参数）
ffmpeg -i a.mp4 -i b.mp4 -filter_complex \
  "[0:v][1:v]xfade=transition=fade:duration=1:offset=5[v]" \
  -map "[v]" -c:v libx264 out.mp4
```

## 字幕

```bash
# 烧录 SRT（Windows 中文字体）
ffmpeg -i input.mp4 -vf "subtitles=sub.srt:force_style='FontName=Microsoft YaHei,FontSize=18'" -c:v libx264 -crf 20 -c:a copy out.mp4

# 外挂字幕转内嵌
ffmpeg -i input.mp4 -i sub.srt -c copy -c:s mov_text out.mp4
```

## 音频处理

```bash
# 响度归一化到 -14 LUFS
ffmpeg -i input.mp4 -af loudnorm=I=-14:TP=-1.5 -c:v copy -c:a aac out.mp4

# BGM 压低 + 人声（BGM -18dB）
ffmpeg -i voice.mp4 -i bgm.mp3 -filter_complex \
  "[1:a]volume=0.15[bgm];[0:a][bgm]amix=inputs=2:duration=first[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac out.mp4

# 降噪
ffmpeg -i input.mp4 -af afftdn=nf=-25 -c:v copy -c:a aac out.mp4
```

## 变速

```bash
# 1.5 倍速（视频+音频）
ffmpeg -i input.mp4 -filter_complex "[0:v]setpts=PTS/1.5[v];[0:a]atempo=1.5[a]" -map "[v]" -map "[a]" out.mp4
```

## 画幅与画面

```bash
# 竖屏 1080x1920
ffmpeg -i input.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -crf 20 -c:a aac out.mp4

# 裁剪画面中心区域
ffmpeg -i input.mp4 -vf "crop=iw/2:ih/2" -c:v libx264 out.mp4
```

## 抽帧 / GIF

```bash
# 每秒抽一帧
ffmpeg -i input.mp4 -vf fps=1 frame_%03d.jpg

# 转 GIF
ffmpeg -i input.mp4 -vf "fps=15,scale=480:-1" -loop 0 out.gif
```

## 录屏

```bash
# Windows 录屏（gdigrab，全屏）
ffmpeg -f gdigrab -framerate 30 -i desktop -c:v libx264 -crf 20 out.mp4
```

## 批量处理

```bash
# 批量转码当前目录所有 mp4（PowerShell）
Get-ChildItem *.mp4 | ForEach-Object {
  ffmpeg -i $_.FullName -c:v libx264 -crf 22 -c:a aac "$($_.BaseName)_out.mp4"
}
```

## 常见坑

- `-c copy` 无法用于参数不匹配的流；拼接前先统一编码参数
- 中文文件名在部分滤镜中报错：先重命名为英文再处理
- 字幕滤镜对中文路径/字体敏感：指定 `FontName=Microsoft YaHei` 或 `SimHei`
- 处理前先备份原始素材
