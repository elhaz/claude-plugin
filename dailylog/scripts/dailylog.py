#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
데일리로그 관리 스크립트

Obsidian 데일리로그 파일을 파싱하고 조작하는 CLI 도구.
- read: 날짜/기간별 읽기
- add: 섹션에 항목 추가
- summary: 통계 요약
"""

import argparse
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from collections import defaultdict


# 데일리로그 파일 경로 패턴
DAILYLOG_PATH_PATTERN = "02_Areas/일지/데일리로그 {year}.md"

# 요일 매핑 (한국어)
WEEKDAYS_KO = ["월", "화", "수", "목", "금", "토", "일"]

# 섹션 목록
SECTIONS = ["회사", "개인", "스크랩", "아이디어"]


def get_dailylog_path(vault_path: Path, year: int) -> Path:
    """연도에 해당하는 데일리로그 파일 경로 반환"""
    return vault_path / DAILYLOG_PATH_PATTERN.format(year=year)


def parse_date(date_str: str) -> datetime:
    """날짜 문자열을 datetime으로 변환

    지원 형식:
    - today, yesterday
    - YYYY-MM-DD
    - MM-DD (현재 연도 기준)
    """
    today = datetime.now()

    if date_str.lower() == "today":
        return today
    elif date_str.lower() == "yesterday":
        return today - timedelta(days=1)

    # YYYY-MM-DD 형식
    if re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        return datetime.strptime(date_str, "%Y-%m-%d")

    # MM-DD 형식 (현재 연도)
    if re.match(r"^\d{2}-\d{2}$", date_str):
        return datetime.strptime(f"{today.year}-{date_str}", "%Y-%m-%d")

    raise ValueError(f"지원하지 않는 날짜 형식: {date_str}")


def get_week_range(date: datetime) -> tuple[datetime, datetime]:
    """주어진 날짜가 속한 주의 시작일(월요일)과 종료일(일요일) 반환"""
    start = date - timedelta(days=date.weekday())
    end = start + timedelta(days=6)
    return start, end


def get_month_range(date: datetime) -> tuple[datetime, datetime]:
    """주어진 날짜가 속한 월의 시작일과 종료일 반환"""
    start = date.replace(day=1)
    # 다음 달 1일에서 하루 빼서 이번 달 마지막 날 구하기
    if date.month == 12:
        end = date.replace(year=date.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end = date.replace(month=date.month + 1, day=1) - timedelta(days=1)
    return start, end


def parse_dailylog(content: str) -> dict:
    """데일리로그 파일 내용을 파싱하여 구조화된 딕셔너리로 반환

    반환 구조:
    {
        "2026-01-08": {
            "weekday": "목",
            "sections": {
                "회사": ["- 항목1", "- 항목2"],
                "개인": ["- 항목1"],
                ...
            },
            "raw": "#### 2026-01-08 (목)\n..."
        },
        ...
    }
    """
    entries = {}

    # 날짜 헤더 패턴: #### YYYY-MM-DD (요일)
    date_pattern = re.compile(r"^####\s+(\d{4}-\d{2}-\d{2})\s+\(([월화수목금토일])\)")
    # 섹션 헤더 패턴: ##### 섹션명
    section_pattern = re.compile(r"^#####\s+(.+)")

    current_date = None
    current_section = None
    current_raw_lines = []

    lines = content.split("\n")

    for i, line in enumerate(lines):
        date_match = date_pattern.match(line)

        if date_match:
            # 이전 날짜 저장
            if current_date:
                entries[current_date]["raw"] = "\n".join(current_raw_lines)

            # 새 날짜 시작
            current_date = date_match.group(1)
            weekday = date_match.group(2)
            current_section = None
            current_raw_lines = [line]

            entries[current_date] = {
                "weekday": weekday,
                "sections": {s: [] for s in SECTIONS},
                "raw": ""
            }
        elif current_date:
            current_raw_lines.append(line)

            section_match = section_pattern.match(line)
            if section_match:
                section_name = section_match.group(1).strip()
                if section_name in SECTIONS:
                    current_section = section_name
            elif current_section and line.strip().startswith("-") and not line.strip().startswith("---"):
                entries[current_date]["sections"][current_section].append(line)
            elif line.startswith("---"):
                # 구분선을 만나면 현재 날짜 종료
                if current_date:
                    entries[current_date]["raw"] = "\n".join(current_raw_lines[:-1])
                current_date = None
                current_section = None

    # 마지막 날짜 저장
    if current_date:
        entries[current_date]["raw"] = "\n".join(current_raw_lines)

    return entries


def read_entries(vault_path: Path, start_date: datetime, end_date: Optional[datetime] = None) -> str:
    """지정된 기간의 데일리로그 항목 읽기"""
    if end_date is None:
        end_date = start_date

    # 시작일과 종료일 사이의 모든 연도 수집
    years = set()
    current = start_date
    while current <= end_date:
        years.add(current.year)
        current += timedelta(days=1)

    # 각 연도별 파일에서 항목 수집
    all_entries = {}
    for year in sorted(years):
        file_path = get_dailylog_path(vault_path, year)
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8")
            entries = parse_dailylog(content)
            all_entries.update(entries)

    # 기간 내 항목 필터링
    result_lines = []
    current = start_date
    while current <= end_date:
        date_str = current.strftime("%Y-%m-%d")
        if date_str in all_entries:
            result_lines.append(all_entries[date_str]["raw"])
            result_lines.append("")  # 빈 줄 추가
        current += timedelta(days=1)

    if not result_lines:
        return f"지정된 기간({start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')})에 해당하는 항목이 없습니다."

    return "\n".join(result_lines).strip()


def generate_day_template(date: datetime) -> str:
    """날짜에 대한 템플릿 생성"""
    weekday = WEEKDAYS_KO[date.weekday()]
    date_str = date.strftime("%Y-%m-%d")

    return f"""#### {date_str} ({weekday})

##### 회사
-

##### 개인
-

##### 스크랩
-

##### 아이디어
-"""


def find_insert_position(content: str, target_date: datetime) -> tuple[int, bool, str]:
    """항목을 삽입할 위치와 날짜 섹션 존재 여부 반환

    반환: (삽입 위치, 날짜 섹션 존재 여부, 주차 헤더)
    """
    lines = content.split("\n")
    date_str = target_date.strftime("%Y-%m-%d")

    # 날짜 헤더 패턴
    date_pattern = re.compile(r"^####\s+(\d{4}-\d{2}-\d{2})")

    # 해당 날짜 찾기
    for i, line in enumerate(lines):
        match = date_pattern.match(line)
        if match and match.group(1) == date_str:
            return i, True, ""

    # 날짜가 없으면 적절한 위치 찾기 (날짜 내림차순 정렬)
    # 월 헤더 아래, 가장 가까운 과거 날짜 앞에 삽입
    month_pattern = re.compile(r"^##\s+(\d+)월")
    week_pattern = re.compile(r"^###\s+(\d+)월\s+(\d+)주차")

    target_month = target_date.month
    target_week = (target_date.day - 1) // 7 + 1

    insert_pos = -1
    week_header = ""

    for i, line in enumerate(lines):
        # 월 헤더 확인
        month_match = month_pattern.match(line)
        if month_match:
            month_num = int(month_match.group(1))
            if month_num == target_month:
                insert_pos = i + 1

        # 주차 헤더 확인
        week_match = week_pattern.match(line)
        if week_match:
            week_month = int(week_match.group(1))
            week_num = int(week_match.group(2))
            if week_month == target_month:
                insert_pos = i + 1
                week_header = line

        # 날짜 확인 - 타겟 날짜보다 과거면 그 앞에 삽입
        date_match = date_pattern.match(line)
        if date_match:
            existing_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
            if existing_date < target_date:
                return i, False, week_header

    return insert_pos if insert_pos > 0 else len(lines), False, week_header


def add_item(vault_path: Path, date: datetime, section: str, item: str) -> str:
    """데일리로그에 항목 추가"""
    if section not in SECTIONS:
        return f"오류: 유효하지 않은 섹션입니다. 사용 가능: {', '.join(SECTIONS)}"

    file_path = get_dailylog_path(vault_path, date.year)

    if not file_path.exists():
        return f"오류: 데일리로그 파일이 존재하지 않습니다: {file_path}"

    content = file_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    date_str = date.strftime("%Y-%m-%d")
    date_pattern = re.compile(r"^####\s+(\d{4}-\d{2}-\d{2})")
    section_pattern = re.compile(r"^#####\s+(.+)")

    # 날짜 섹션 찾기
    date_line_idx = -1
    for i, line in enumerate(lines):
        match = date_pattern.match(line)
        if match and match.group(1) == date_str:
            date_line_idx = i
            break

    # 날짜 섹션이 없으면 생성
    if date_line_idx == -1:
        insert_pos, _, _ = find_insert_position(content, date)
        template = generate_day_template(date)
        lines.insert(insert_pos, "")
        lines.insert(insert_pos + 1, template)
        lines.insert(insert_pos + 2, "")
        lines.insert(insert_pos + 3, "---")
        content = "\n".join(lines)
        lines = content.split("\n")

        # 다시 찾기
        for i, line in enumerate(lines):
            match = date_pattern.match(line)
            if match and match.group(1) == date_str:
                date_line_idx = i
                break

    # 섹션 찾기
    section_line_idx = -1
    next_section_idx = len(lines)
    in_target_date = False

    for i in range(date_line_idx, len(lines)):
        line = lines[i]

        # 다음 날짜나 구분선을 만나면 종료
        if i > date_line_idx and (date_pattern.match(line) or line.strip() == "---"):
            next_section_idx = i
            break

        section_match = section_pattern.match(line)
        if section_match:
            section_name = section_match.group(1).strip()
            if section_name == section:
                section_line_idx = i
            elif section_line_idx != -1:
                # 다음 섹션 시작
                next_section_idx = i
                break

    if section_line_idx == -1:
        return f"오류: {date_str}에서 '{section}' 섹션을 찾을 수 없습니다."

    # 항목 추가 위치 결정 (섹션의 마지막 항목 다음)
    insert_idx = section_line_idx + 1
    for i in range(section_line_idx + 1, next_section_idx):
        line = lines[i].strip()
        if line.startswith("-") or line == "":
            insert_idx = i + 1
        else:
            break

    # 현재 시간 타임스탬프 생성
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 항목 형식 정리 (타임스탬프 포함)
    if item.startswith("-"):
        item = item[1:].strip()  # 앞의 - 제거
    item = f"- {timestamp} {item}"

    lines.insert(insert_idx, item)

    # 파일 저장
    new_content = "\n".join(lines)
    file_path.write_text(new_content, encoding="utf-8")

    return f"항목이 추가되었습니다: {date_str} > {section}\n{item}"


def generate_summary(vault_path: Path, start_date: datetime, end_date: datetime) -> str:
    """기간별 통계 요약 생성"""
    # 연도별 파일 수집
    years = set()
    current = start_date
    while current <= end_date:
        years.add(current.year)
        current += timedelta(days=1)

    # 모든 항목 수집
    all_entries = {}
    for year in sorted(years):
        file_path = get_dailylog_path(vault_path, year)
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8")
            entries = parse_dailylog(content)
            all_entries.update(entries)

    # 기간 내 항목 필터링 및 통계 계산
    section_counts = defaultdict(int)
    section_items = defaultdict(list)
    links = []
    days_with_entries = 0

    current = start_date
    while current <= end_date:
        date_str = current.strftime("%Y-%m-%d")
        if date_str in all_entries:
            days_with_entries += 1
            entry = all_entries[date_str]

            for section, items in entry["sections"].items():
                for item in items:
                    if item.strip() and item.strip() != "-":
                        section_counts[section] += 1
                        section_items[section].append(f"{date_str}: {item.strip()}")

                        # 링크 추출
                        link_matches = re.findall(r"\[\[([^\]]+)\]\]", item)
                        for link in link_matches:
                            links.append(f"[[{link}]]")

        current += timedelta(days=1)

    # 요약 출력 생성
    total_days = (end_date - start_date).days + 1

    result = []
    result.append(f"## 기간 요약: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
    result.append("")
    result.append(f"**기간**: {total_days}일 중 {days_with_entries}일 기록")
    result.append("")

    # 섹션별 통계
    result.append("### 섹션별 항목 수")
    result.append("")
    result.append("| 섹션 | 항목 수 |")
    result.append("|------|---------|")
    for section in SECTIONS:
        count = section_counts.get(section, 0)
        result.append(f"| {section} | {count} |")
    result.append("")

    # 주요 링크
    if links:
        unique_links = list(dict.fromkeys(links))  # 중복 제거, 순서 유지
        result.append("### 언급된 문서 링크")
        result.append("")
        for link in unique_links[:20]:  # 최대 20개
            result.append(f"- {link}")
        if len(unique_links) > 20:
            result.append(f"- ... 외 {len(unique_links) - 20}개")
        result.append("")

    # 섹션별 항목 목록 (접힌 상태)
    result.append("### 섹션별 상세 항목")
    result.append("")
    for section in SECTIONS:
        items = section_items.get(section, [])
        if items:
            result.append(f"> [!note]- {section} ({len(items)}건)")
            for item in items[:30]:  # 최대 30개
                result.append(f"> {item}")
            if len(items) > 30:
                result.append(f"> ... 외 {len(items) - 30}건")
            result.append("")

    return "\n".join(result)


def main():
    parser = argparse.ArgumentParser(
        description="Obsidian 데일리로그 관리 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 오늘 항목 읽기
  dailylog.py read today

  # 특정 날짜 읽기
  dailylog.py read 2026-01-15

  # 이번 주 읽기
  dailylog.py read --week

  # 항목 추가
  dailylog.py add --section 회사 "회의 참석"

  # 특정 날짜에 항목 추가
  dailylog.py add --section 개인 --date 2026-01-15 "운동 1시간"

  # 이번 주 요약
  dailylog.py summary --week
"""
    )

    parser.add_argument("--vault", type=str, default=".",
                        help="Obsidian Vault 경로 (기본값: 현재 디렉토리)")

    subparsers = parser.add_subparsers(dest="command", help="명령어")

    # read 서브커맨드
    read_parser = subparsers.add_parser("read", help="데일리로그 읽기")
    read_parser.add_argument("date", nargs="?", default="today",
                             help="날짜 (today, yesterday, YYYY-MM-DD)")
    read_parser.add_argument("--from", dest="from_date", type=str,
                             help="시작 날짜")
    read_parser.add_argument("--to", dest="to_date", type=str,
                             help="종료 날짜")
    read_parser.add_argument("--week", action="store_true",
                             help="이번 주 전체")
    read_parser.add_argument("--month", action="store_true",
                             help="이번 달 전체")

    # add 서브커맨드
    add_parser = subparsers.add_parser("add", help="항목 추가")
    add_parser.add_argument("item", type=str, help="추가할 항목 내용")
    add_parser.add_argument("--section", "-s", type=str, required=True,
                            choices=SECTIONS, help="섹션 (회사, 개인, 스크랩, 아이디어)")
    add_parser.add_argument("--date", "-d", type=str, default="today",
                            help="날짜 (기본값: today)")

    # summary 서브커맨드
    summary_parser = subparsers.add_parser("summary", help="기간별 요약")
    summary_parser.add_argument("--from", dest="from_date", type=str,
                                help="시작 날짜")
    summary_parser.add_argument("--to", dest="to_date", type=str,
                                help="종료 날짜")
    summary_parser.add_argument("--week", action="store_true",
                                help="이번 주")
    summary_parser.add_argument("--month", action="store_true",
                                help="이번 달")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    vault_path = Path(args.vault).resolve()

    if args.command == "read":
        today = datetime.now()

        if args.week:
            start_date, end_date = get_week_range(today)
        elif args.month:
            start_date, end_date = get_month_range(today)
        elif args.from_date:
            start_date = parse_date(args.from_date)
            end_date = parse_date(args.to_date) if args.to_date else start_date
        else:
            start_date = parse_date(args.date)
            end_date = start_date

        result = read_entries(vault_path, start_date, end_date)
        print(result)

    elif args.command == "add":
        date = parse_date(args.date)
        result = add_item(vault_path, date, args.section, args.item)
        print(result)

    elif args.command == "summary":
        today = datetime.now()

        if args.week:
            start_date, end_date = get_week_range(today)
        elif args.month:
            start_date, end_date = get_month_range(today)
        elif args.from_date:
            start_date = parse_date(args.from_date)
            end_date = parse_date(args.to_date) if args.to_date else today
        else:
            # 기본값: 이번 주
            start_date, end_date = get_week_range(today)

        result = generate_summary(vault_path, start_date, end_date)
        print(result)


if __name__ == "__main__":
    main()
