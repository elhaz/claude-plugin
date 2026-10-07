---
name: YouTube Transcript to Obsidian
description: 이 스킬은 사용자가 "YouTube 자막 추출", "YouTube 영상을 마크다운으로", "yt-dlp 사용법", "VTT 변환", "YouTube 자막 다운로드", "vtt_to_markdown 사용법", "YouTube Obsidian 문서화"를 요청할 때 사용한다. YouTube 자막을 Obsidian 스타일 마크다운 문서로 변환하는 워크플로우 가이드를 제공한다.
version: 1.1.0
---

# YouTube 자막 → Obsidian 문서 변환 가이드

YouTube 영상(쇼츠·일반 영상·커뮤니티 게시물)을 Obsidian 스타일 노트로 정리한다.

> [!important] 절차의 단일 출처는 명령 파일이다
> 실제 절차·규칙은 **`commands/youtube-extract.md`** 에만 적는다. 이 스킬은 무엇을 하는지와 어디를 보면 되는지만 안내한다.
> 작업할 때는 `/youtube-extract <URL>` 을 쓰거나, 명령 파일 `${CLAUDE_PLUGIN_ROOT}/commands/youtube-extract.md` 를 Read 해서 그대로 따른다. 이 스킬의 내용으로 절차를 대신하지 않는다.
> 쓰다가 새 규칙이 생기면 이 파일이나 메모리가 아니라 명령 파일을 고친다.

## 하는 일 (요약)

- 자막 다운로드(한국어는 `ko-orig`) → 스크립트로 마크다운 변환 → Obsidian 스타일로 재구성
- 설명란에 블로그·가이드 전문이 있으면 그 글을 기준으로 정리
- 같은 채널 폴더 → 분명한 주제 폴더 → `00_Inbox/` 순으로 배치하고 인덱스에 링크
- 데일리로그 스크랩 칸에 한 줄 (스크립트가 있는 환경만)
- 보고 전 완료 확인 (링크·그림 존재, cardlink YAML, 인덱스·데일리로그 반영)

Vault 루트는 환경변수 `OBSIDIAN_VAULT`, 미설정 시 현재 작업 디렉토리.

## 참조 파일

- **`commands/youtube-extract.md`** — 전체 절차 (단일 출처)
- **`references/cardlink-format.md`** — cardlink 형식과 YAML 특수문자 처리
- **`references/yt-dlp-options.md`** — yt-dlp 옵션 상세
- **`references/troubleshooting.md`** — 문제 해결
- **`scripts/vtt_to_markdown.py`** — VTT → 마크다운 변환 (VTT 를 Read 로 직접 읽지 않는다)
