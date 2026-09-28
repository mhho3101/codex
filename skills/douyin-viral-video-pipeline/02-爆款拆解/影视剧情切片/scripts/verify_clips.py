"""按实际结果清单检查文件；时长要求只用于成片。"""
import argparse
import json
import sys
from pathlib import Path
from clip_checks import executable, probe, check_media


def verify(manifest_path, ffprobe):
    path = Path(manifest_path).resolve()
    manifest = json.loads(path.read_text(encoding='utf-8-sig'))
    if manifest.get('version') != 2:
        raise ValueError('旧清单只有计划，没有实际执行结果，请用新版切割脚本重新输出到新目录')
    errors = []
    expected = 'complete' if manifest['merge_requested'] else 'pieces_only'
    if manifest.get('status') != expected:
        errors.append('这次切割未全部完成')
    segments = manifest['segments']
    if not segments or len(segments) != manifest['expected_count']:
        errors.append('清单中的条数不完整')
    def inspect(relative, limits=None):
        actual = (path.parent/relative).resolve()
        if not actual.is_relative_to(path.parent):
            raise ValueError('清单引用了输出目录以外的文件')
        check_media(probe(actual, ffprobe), manifest['source_info'], limits)
    for seg in segments:
        try:
            if seg.get('status') != expected:
                raise ValueError(seg.get('error', '本条未完成'))
            if len(seg['pieces']) != len(seg['clips']):
                raise ValueError('片段数量不完整')
            for piece in seg['pieces']:
                inspect(piece)
            if manifest['merge_requested']:
                if not seg.get('final'):
                    raise ValueError('缺少成片路径')
                inspect(seg['final'], manifest['limits'])
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(f"第 {seg.get('num', '?')} 条：{exc}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', nargs='?', help='输出目录；里面必须只有一份结果清单')
    parser.add_argument('--manifest', help='明确指定结果清单')
    parser.add_argument('--ffprobe', '--ffmpeg', dest='ffprobe', default='ffprobe', help='ffprobe 命令或完整路径；旧参数 --ffmpeg 仍兼容')
    args = parser.parse_args()
    try:
        tool = executable(args.ffprobe)
        if args.manifest:
            path = Path(args.manifest)
        else:
            paths = list(Path(args.directory or '.').glob('*_segments_manifest.json'))
            if len(paths) != 1:
                raise ValueError('需要唯一一份结果清单；请使用 --manifest 指定')
            path = paths[0]
        errors = verify(path, tool)
        print(json.dumps(dict(passed=not errors, errors=errors), ensure_ascii=False, indent=2))
        return 1 if errors else 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'无法验证：{exc}')
        return 2


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    sys.exit(main())
