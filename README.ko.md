# AGENTS.md Check

[English](README.md)

`AGENTS.md` 파일에서 병합 충돌 표시와 보이지 않는 문자 같은 기계적인 문제를 찾는 도구입니다. 파일을 고치거나 외부로 보내지 않습니다.

## 시작하기

Python 3.9 이상이 필요합니다. 별도 패키지는 필요하지 않습니다.

```sh
git clone https://github.com/yangdoh/agents-md-check.git
cd agents-md-check
python3 agents_md_check.py /path/to/project
```

`/path/to/project`는 검사할 폴더 경로로 바꿉니다. 폴더 안의 `AGENTS.md` 파일을 찾아 검사합니다.

```sh
python3 agents_md_check.py /path/to/project --json
python3 agents_md_check.py /path/to/project --require-files
```

`--json`은 프로그램에서 읽기 좋은 결과를 출력합니다. `--require-files`는 파일을 하나도 찾지 못했을 때 이를 문제로 표시합니다.

## 결과 읽기

- 종료 코드 `0`: 발견된 문제가 없습니다.
- 종료 코드 `1`: 하나 이상의 점검 항목이 발견됐습니다.
- 종료 코드 `2`: 입력이 잘못됐거나 검사가 끝나지 않았습니다.

검사 항목에는 병합 충돌 표시, 일부 보이지 않는 양방향 문자, 빈 파일, 잘못된 UTF-8, 긴 중복 문장, 크기 경고가 포함됩니다. 심볼릭 링크 파일은 따라가지 않고 표시합니다.

이 도구는 지시의 정확성이나 안전성, AI의 실제 지시 이행 여부를 판단하지 않습니다. 경고를 직접 확인하세요.

`.gitignore`는 적용하지 않습니다. 검사할 폴더를 신중하게 고르세요. 1 MiB보다 큰 파일은 내용을 검사하지 않으며 전체 검사는 미완료로 표시됩니다. 출력에 개인 경로가 포함될 수 있으므로 공유 전에 확인하세요.

## 의견 보내기

[문제나 개선 아이디어를 알려주세요](https://github.com/yangdoh/agents-md-check/issues/new/choose). 한국어로 작성해도 됩니다. GitHub 계정이 필요하며 제보 내용은 공개됩니다. 개인 지시사항, 경로, 비밀정보는 지우고 올려주세요.

## 기여와 라이선스

문제 제보와 기여 방법은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참고하세요. 라이선스는 [MIT](LICENSE)입니다.
