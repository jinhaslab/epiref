# docs/json — 구조화 데이터 (non-HTML)

이 폴더는 epiref 의 **HTML 이 아닌 정보(구조화 데이터)** 를 JSON 으로 저장한다.

## 목적
- `docs/` 의 `*_population.html`, `*_process.html`, 향후 `*_exposure.html` 등에서 뽑아낸
  정보를 레코드별 JSON 으로 보관.
- GitHub Pages(`jinhaslab.github.io/epiref/`)로 배포되므로
  `https://jinhaslab.github.io/epiref/json/<fid>.json` 형태의 **링크로 접근** 가능.
- Django 사이트(kosha.ai.kr/epiedit)는 무거운 데이터를 직접 서빙하지 않고
  이 링크만 참조 → 사이트 경량 유지.

## 파일 규칙 (제안)
- 파일명: `<fid>.json` (예: `kosha2000_003_004.json`)
- HTML 원본은 `docs/` 에, 그 HTML 에서 파싱한 구조화 정보만 여기 JSON 으로.
