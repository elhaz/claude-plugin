#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VTT 자막 파일을 Obsidian 마크다운 문서로 변환하는 스크립트

사용법:
    PYTHONIOENCODING=utf-8 uv run scripts/vtt_to_markdown.py <VTT파일경로> [--delete-vtt]

옵션:
    --delete-vtt: 변환 완료 후 원본 VTT 파일 삭제
"""

import re
import sys
import io
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Windows 콘솔 인코딩 문제 해결
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def get_video_metadata(video_url):
    """yt-dlp를 사용하여 YouTube 영상 메타데이터 가져오기"""
    try:
        result = subprocess.run(
            ['yt-dlp', '--dump-json', '--skip-download', video_url],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return {
                'title': data.get('title', ''),
                'description': data.get('description', '')[:200] if data.get('description') else '',
                'thumbnail': data.get('thumbnail', ''),
                'channel': data.get('channel', ''),
                'upload_date': data.get('upload_date', '')
            }
    except Exception as e:
        print(f"[경고] 메타데이터 가져오기 실패: {e}")
    return None


def sanitize_yaml_string(text):
    """cardlink 블록용 YAML 안전 문자열로 변환

    Auto Card Link 의 cardlink 블록은 값을 따옴표로 감싸지 않는 것이
    Vault 컨벤션이므로, 감싸는 대신 위험 문자를 제거·치환한다.

    YAML 은 대부분의 특수문자를 **값의 첫 글자일 때만** 특수하게 해석하지만
    (`[` `{` `&` `*` `!` `%` `|` `>` `@` 백틱), `#` 은 앞에 공백이 오면
    위치와 무관하게 주석으로 잘린다. 아래 처리는 그 두 경우를 모두 막는다.
    """
    if not text:
        return ''

    # 개행·따옴표·말줄임표 제거
    text = text.replace('"', '').replace("'", '').replace('...', '')
    text = text.replace('\n', ' ').replace('\r', ' ')

    # 괄호류는 위치와 무관하게 소괄호로 치환 (값 중간이라도 가독성 통일)
    for src, dst in (('[', '('), (']', ')'), ('{', '('), ('}', ')')):
        text = text.replace(src, dst)

    # ':' 는 뒤에 공백이 오면 키-값 구분자로 오인되므로 '-' 로 치환
    text = re.sub(r':(?=\s)', ' -', text)
    text = text.replace(':', ' -')

    # ' #' 는 위치와 무관하게 주석 시작이므로 '#' 를 제거
    text = text.replace('#', '')

    # 파이프·부등호는 블록 스칼라 오인 방지
    text = text.replace('|', '/').replace('>', '').replace('<', '')

    text = text.replace('&', 'and')

    # 연속 공백 정리
    text = re.sub(r'\s+', ' ', text).strip()

    # 남은 선두 특수문자 제거 (값 첫 글자일 때만 의미를 갖는 문자들)
    text = text.lstrip('*!%@`-? ').strip()

    return text


def parse_vtt_to_markdown(vtt_file_path):
    """VTT 파일을 읽어서 마크다운 형식으로 변환"""

    with open(vtt_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    # 자막 엔트리 파싱
    entries = []
    current_time = None
    current_text = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # 타임스탬프 라인 감지
        if ' --> ' in line:
            # 이전 엔트리 저장
            if current_time and current_text:
                text = ' '.join(current_text)
                # 인라인 타임스탬프 제거 (<00:00:00.880> 형태)
                text = re.sub(r'<\d{2}:\d{2}:\d{2}\.\d{3}>', '', text)
                # <c> 태그 제거
                text = re.sub(r'</?c>', '', text)
                # 공백 정리
                text = re.sub(r'\s+', ' ', text).strip()

                if text and text not in ['[음악]', '[Music]', 'Ah.', '[박수]', '[Applause]']:
                    entries.append({
                        'time': current_time,
                        'text': text
                    })

            # 새로운 타임스탬프 파싱
            time_match = re.match(r'(\d{2}:\d{2}:\d{2}\.\d{3})', line)
            if time_match:
                current_time = time_match.group(1)
                current_text = []

        # 텍스트 라인
        elif line and not line.startswith('WEBVTT') and not line.startswith('Kind:') and not line.startswith('Language:') and 'align:start' not in line:
            current_text.append(line)

        i += 1

    # 마지막 엔트리 저장
    if current_time and current_text:
        text = ' '.join(current_text)
        text = re.sub(r'<\d{2}:\d{2}:\d{2}\.\d{3}>', '', text)
        text = re.sub(r'</?c>', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        if text and text not in ['[음악]', '[Music]', 'Ah.', '[박수]', '[Applause]']:
            entries.append({
                'time': current_time,
                'text': text
            })

    # 중복 제거 및 텍스트 병합
    cleaned_entries = []
    prev_text = None

    for entry in entries:
        current_text = entry['text']

        # 이전 텍스트와 완전히 같으면 스킵
        if prev_text and current_text == prev_text:
            continue

        # 이전 텍스트가 현재 텍스트에 완전히 포함되면, 현재 텍스트로 대체
        if prev_text and prev_text in current_text:
            cleaned_entries[-1] = entry
            prev_text = current_text
            continue

        # 현재 텍스트가 이전 텍스트에 완전히 포함되면 스킵
        if prev_text and current_text in prev_text:
            continue

        # 부분 중복 제거
        if prev_text:
            max_overlap = min(len(prev_text), len(current_text))
            overlap_found = False

            for overlap_len in range(max_overlap, 4, -1):
                if prev_text[-overlap_len:] == current_text[:overlap_len]:
                    new_text = current_text[overlap_len:].strip()
                    if new_text:
                        cleaned_entries.append({
                            'time': entry['time'],
                            'text': new_text
                        })
                        prev_text = new_text
                    overlap_found = True
                    break

            if not overlap_found:
                cleaned_entries.append(entry)
                prev_text = current_text
        else:
            cleaned_entries.append(entry)
            prev_text = current_text

    return cleaned_entries


def format_timestamp(timestamp):
    """타임스탬프를 분:초 형식으로 변환"""
    parts = timestamp.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])

    total_minutes = hours * 60 + minutes

    if total_minutes > 0:
        return f"{total_minutes:02d}:{seconds:05.2f}"
    else:
        return f"00:{seconds:05.2f}"


def extract_video_info(vtt_filename):
    """VTT 파일명에서 비디오 정보 추출"""
    # 파일명 패턴: "제목 [VIDEO_ID].ko.vtt" 또는 "제목 [VIDEO_ID].en.vtt"
    match = re.search(r'\[([^\]]+)\]\.(ko|en)\.vtt$', vtt_filename)
    if match:
        video_id = match.group(1)
        lang = match.group(2)
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        # 제목 추출
        title = re.sub(r'\s*\[([^\]]+)\]\.(ko|en)\.vtt$', '', vtt_filename)
        return video_url, title, lang
    else:
        return None, vtt_filename.replace('.vtt', ''), 'unknown'


def create_cardlink(video_url, metadata):
    """Obsidian cardlink 형식 생성"""
    if not metadata:
        return f"- **출처**: {video_url}"

    title = sanitize_yaml_string(metadata.get('title', ''))
    description = sanitize_yaml_string(metadata.get('description', ''))
    thumbnail = metadata.get('thumbnail', '')

    return f"""```cardlink
url: {video_url}
title: {title}
description: {description}
host: www.youtube.com
favicon: https://www.youtube.com/s/desktop/626d9c6b/img/favicon_32x32.png
image: {thumbnail}
```"""


def create_markdown(entries, video_url, video_title, metadata=None, lang='ko'):
    """마크다운 문서 생성"""

    now = datetime.now().strftime('%Y-%m-%d')

    cardlink = create_cardlink(video_url, metadata)

    lang_text = "한국어" if lang == 'ko' else "영어 (번역 필요)"

    markdown = f"""---
생성일: {now}
마지막수정일: {now}
---

# {video_title}

## 영상 정보

{cardlink}

- **언어**: {lang_text} (자동 생성 자막)

## 자막 내용

"""

    for entry in entries:
        time_formatted = format_timestamp(entry['time'])
        markdown += f"**[{time_formatted}]** {entry['text']}\n\n"

    markdown += """---

**태그**: #유튜브 #자막
"""

    return markdown


def main():
    # 커맨드라인 인자 확인
    if len(sys.argv) < 2:
        print("[오류] VTT 파일 경로를 지정해주세요.")
        print("사용법: PYTHONIOENCODING=utf-8 uv run scripts/vtt_to_markdown.py <VTT파일경로> [--delete-vtt]")
        sys.exit(1)

    vtt_file_path = Path(sys.argv[1])
    delete_vtt = '--delete-vtt' in sys.argv

    if not vtt_file_path.exists():
        print(f"[오류] 파일을 찾을 수 없습니다: {vtt_file_path}")
        sys.exit(1)

    # 비디오 정보 추출
    video_url, video_title, lang = extract_video_info(vtt_file_path.name)

    if not video_url:
        print("[경고] 비디오 URL을 추출할 수 없습니다. 파일명을 제목으로 사용합니다.")
        video_url = ""

    print(f"[시작] VTT 파일 파싱 중: {vtt_file_path.name}")
    print(f"       제목: {video_title}")
    print(f"       URL: {video_url}")
    print(f"       언어: {lang}")

    # 메타데이터 가져오기
    metadata = None
    if video_url:
        print("[정보] YouTube 메타데이터 가져오는 중...")
        metadata = get_video_metadata(video_url)
        if metadata:
            print(f"       채널: {metadata.get('channel', 'N/A')}")

    # VTT 파싱
    entries = parse_vtt_to_markdown(vtt_file_path)
    print(f"[완료] 총 {len(entries)}개의 자막 엔트리 파싱 완료")

    # 마크다운 생성
    markdown = create_markdown(entries, video_url, video_title, metadata, lang)

    # 출력 파일 (같은 폴더에 저장)
    output_file = vtt_file_path.parent / f"{video_title}.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f"[완료] 마크다운 파일 생성: {output_file.name}")
    print(f"       위치: {output_file.parent}")

    # VTT 파일 삭제
    if delete_vtt:
        try:
            vtt_file_path.unlink()
            print(f"[삭제] VTT 파일 삭제됨: {vtt_file_path.name}")
        except Exception as e:
            print(f"[오류] VTT 파일 삭제 실패: {e}")

    # 영어 자막인 경우 번역 안내
    if lang == 'en':
        print("\n[안내] 영어 자막입니다. Claude에게 번역을 요청하세요:")
        print(f"       '이 문서를 한국어로 번역해줘: {output_file}'")


if __name__ == "__main__":
    main()
