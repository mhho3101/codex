"""Shared configuration and media checks (standard library only)."""
import json
import math
import re
import shutil
import subprocess
from pathlib import Path


def executable(value):
    found = shutil.which(value)
    if not found:
        raise ValueError(f"找不到工具：{value}")
    return found


def probe(path, ffprobe):
    r = subprocess.run([ffprobe, '-v', 'error', '-show_format', '-show_streams',
                        '-of', 'json', str(path)], capture_output=True, encoding='utf-8')
    if r.returncode:
        raise ValueError(f"视频无法读取：{path}；{r.stderr[-300:]}")
    data = json.loads(r.stdout)
    duration = float(data.get('format', {}).get('duration', 0))
    video = next((s for s in data.get('streams', []) if s['codec_type'] == 'video'), None)
    if not video or not math.isfinite(duration) or duration <= 0:
        raise ValueError(f"没有有效的视频或时长：{path}")
    return dict(duration=duration, width=video['width'], height=video['height'],
                codec=video['codec_name'], audio=any(s['codec_type'] == 'audio' for s in data['streams']))


def number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"时间必须是有限数字：{value}")
    return value


def name(value):
    if not isinstance(value, str) or not value.strip() or re.search(r'[<>:"/\\|?*\x00-\x1f]', value) or value.endswith((' ', '.')):
        raise ValueError(f"文件名不合法：{value}")
    if re.fullmatch(r'(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?', value):
        raise ValueError(f"Windows 保留文件名：{value}")


def validate(cfg, source):
    name(cfg['movie_name'])
    lo = number(cfg.get('min_duration', 50))
    hi = number(cfg.get('max_duration', 75))
    head, tail = number(cfg['head_end']), number(cfg['tail_start'])
    if not 0 < lo <= hi or not 0 <= head < tail <= source['duration']:
        raise ValueError('时长要求或片头片尾范围不合法')
    if not isinstance(cfg['segments'], list) or not cfg['segments']:
        raise ValueError('segments 不能为空')
    seen, spans = set(), []
    for seg in cfg['segments']:
        n = seg['num']
        if isinstance(n, bool) or not isinstance(n, int) or n < 1 or n in seen:
            raise ValueError('编号必须是互不重复的正整数')
        seen.add(n)
        name(seg['title'])
        clips = seg['clips']
        if not 3 <= len(clips) <= 7 and not (1 <= len(clips) <= 2 and str(seg.get('_note', '')).strip()):
            raise ValueError(f'第 {n} 条需要 3–7 个片段；例外必须填写 _note 说明')
        durations = []
        for clip in clips:
            if len(clip) != 2:
                raise ValueError('每段必须只有起点和终点')
            a, b = map(number, clip)
            if not head <= a < b <= tail:
                raise ValueError(f'第 {n} 条片段越界或起止时间倒置：{clip}')
            spans.append((a, b, n))
            durations.append(b-a)
        if not lo <= sum(durations) <= hi:
            raise ValueError(f'第 {n} 条计划时长 {sum(durations):.2f} 秒，不在 {lo}–{hi} 秒内')
        for narration in seg.get('narrations', []):
            idx = narration.get('clip', 1)
            if isinstance(idx, bool) or not isinstance(idx, int) or not 1 <= idx <= len(clips):
                raise ValueError('旁白引用的片段编号不存在')
            if not 0 <= number(narration.get('after_sec', 3)) < durations[idx-1]:
                raise ValueError('旁白时间超出片段')
    spans.sort()
    for prev, cur in zip(spans, spans[1:]):
        if cur[0] < prev[1]:
            raise ValueError(f'第 {prev[2]}、{cur[2]} 条存在重复画面时间：{prev[:2]} / {cur[:2]}')


def check_media(info, source, limits=None):
    if (info['width'], info['height']) != (source['width'], source['height']):
        raise ValueError('输出分辨率与原片不一致')
    if source['audio'] and not info['audio']:
        raise ValueError('原片有声音，输出却没有音轨')
    if limits and not limits[0] - .15 <= info['duration'] <= limits[1] + .15:
        raise ValueError(f"成片 {info['duration']:.2f} 秒，不符合 {limits[0]}–{limits[1]} 秒要求；请调整选段或使用 --reencode")
