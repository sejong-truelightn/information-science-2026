#!/usr/bin/env python3
"""README의 업데이트 날짜를 각 파일의 마지막 커밋 날짜로 맞춘다.

README 안에 이런 표시를 넣어 두면 그 자리의 날짜가 자동으로 갱신된다:

    <sub><!--date:4차시_Q러닝과_벨만방정식.html-->2026-09-04 업데이트</sub>

주석 안의 경로가 날짜를 가져올 원본 파일이다.
"""
import re, subprocess, sys, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
README = ROOT / 'README.md'
MARK = re.compile(r'(<!--date:(?P<f>[^>]+?)-->)\s*(?:\d{4}-\d{2}-\d{2} 업데이트)?')

def staged_files():
    # -z 로 받아야 한글 경로가 이스케이프되지 않는다
    out = subprocess.run(['git', 'diff', '--cached', '--name-only', '-z'],
                         cwd=ROOT, capture_output=True, text=True).stdout
    return {f for f in out.split('\0') if f}

def last_commit_date(path):
    out = subprocess.run(
        ['git', 'log', '-1', '--format=%cd', '--date=format:%Y-%m-%d', '--', path],
        cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return out or None

def main():
    text = README.read_text(encoding='utf-8')
    missing = []
    # 이번 커밋에 함께 올라가는 파일은 아직 커밋 기록이 없으니 오늘 날짜로 본다
    staged = staged_files()
    today = datetime.date.today().isoformat()

    def sub(m):
        f = m.group('f')
        if not (ROOT / f).exists():
            missing.append(f'{f} — 파일 없음')
            return m.group(0)
        d = today if f in staged else last_commit_date(f)
        if not d:
            missing.append(f'{f} — 커밋 기록 없음')
            return m.group(0)
        return f'{m.group(1)}{d} 업데이트'

    new = MARK.sub(sub, text)
    for w in missing:
        print('경고:', w, file=sys.stderr)
    if new != text:
        README.write_text(new, encoding='utf-8')
        print('README 날짜를 갱신했습니다.')
    else:
        print('바뀐 날짜가 없습니다.')

if __name__ == '__main__':
    main()
