#!/usr/bin/env python3
"""방금 만든 커밋의 메시지를 README의 '최근 업데이트' 목록에 한 줄 추가한다.

README 안의 이 블록 사이에 쌓인다:

    <!--changelog-->
    - **2026-09-04** · 4차시 — γ 값 비교 슬라이드 추가
    <!--/changelog-->

강의자료·노트북(= README에 <!--date:파일--> 로 등록된 파일)이 바뀐 커밋만 기록한다.
"""
import re, subprocess, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
README = ROOT / 'README.md'
KEEP = 12                       # 목록에 남길 줄 수
BLOCK = re.compile(r'(<!--changelog-->\n)(.*?)(<!--/changelog-->)', re.S)
LABEL = re.compile(r'^(\d+차시|실습\s?\d+)')

def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT,
                          capture_output=True, text=True).stdout

def head_files():
    out = git('show', '--name-only', '--format=', '-z', 'HEAD')
    return [f for f in out.split('\0') if f]

def label_of(path):
    name = pathlib.PurePath(path).name
    m = LABEL.match(name)
    return m.group(1).replace(' ', ' ') if m else pathlib.PurePath(name).stem

def main():
    text = README.read_text(encoding='utf-8')
    block = BLOCK.search(text)
    if not block:
        return                                  # 블록이 없으면 아무것도 안 한다

    tracked = set(re.findall(r'<!--date:([^>]+?)-->', text))
    changed = [f for f in head_files() if f in tracked]
    if not changed:
        return                                  # 자료 변경이 없는 커밋은 기록하지 않는다

    subject = git('log', '-1', '--format=%s').strip()
    date    = git('log', '-1', '--format=%cd', '--date=format:%Y-%m-%d').strip()
    labels  = []
    for f in changed:
        l = label_of(f)
        if l not in labels:
            labels.append(l)

    # 메시지가 이미 "4차시: ..." 처럼 시작하면 라벨을 겹쳐 적지 않는다
    for l in labels:
        m = re.match(r'^' + re.escape(l) + r'\s*[:：·—-]\s*', subject)
        if m:
            subject = subject[m.end():]
            break

    line = f'- **{date}** · {" · ".join(labels)} — {subject}'
    old  = [l for l in block.group(2).strip().split('\n') if l.strip()]
    if old and old[0] == line:
        return
    lines = [line] + [l for l in old if l != line]
    new_block = block.group(1) + '\n'.join(lines[:KEEP]) + '\n' + block.group(3)
    README.write_text(text[:block.start()] + new_block + text[block.end():], encoding='utf-8')

if __name__ == '__main__':
    main()
