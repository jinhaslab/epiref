# docs/json — 구조화 데이터 (fid 병합 JSON)

이 폴더는 epiref 역학조사 보고서의 **구조화 정보**를 보고서별 JSON 하나로 보관한다.
`docs/` 의 원본(PDF, `*_population.html`, `*_process.html`)과 별개로,
ote 추출 파이프라인이 만든 JSON 4종을 **fid 기준으로 병합**한 결과다.

## 파일 규칙 · Foreign Key
- 파일명: **`<fid>.json`** (예: `kosha2000_003_004.json`)
- **fid = 파일명 = 공통키(foreign key)**. 형식은 `koshaYYYY_PPP_QQQ`
  (YYYY=년도, PPP_QQQ=보고서 페이지 범위)이며,
  `docs/` 의 PDF/HTML 원본(`kosha2000_003_004.pdf` 등)과 1:1로 대응한다.
- GitHub Pages 배포: `https://jinhaslab.github.io/epiref/json/<fid>.json` 로 접근.
  Django 사이트(kosha.ai.kr/epiedit)는 이 링크만 참조 → 사이트 경량 유지.

## 레코드 구조
```json
{
  "fid":   "kosha2000_003_004",   // 공통키(=파일명)
  "year":  2000,
  "page":  "003_004",
  "title": "산업기 생산부서의 취부작업 근로자에 발생한 폐암",
  "summary":    { ... },   // 메인 요약
  "population": { ... },   // 개인 특성 / 노출 유해인자
  "exposure":   { ... },   // 노출 기존값 (단위 미포함)
  "process":    { ... }    // 공정 / 작업 정보
}
```
각 섹션은 **해당 소스가 있는 경우에만** 포함된다(일부 보고서는 섹션이 빠질 수 있음).

### 섹션별 출처(provenance)
| 섹션 | 의미 | 원본 소스 (ote 파이프라인) |
|---|---|---|
| `summary`    | 제목·성별·나이·직종·질병·직업관련성·개요·작업환경·의학적_소견·결론 | `kosha_final/<fid>.json` |
| `population` | 직종·질병·확진나이·**생년월일**·성별·노출 유해인자·노출시기/기간·흡연/음주/질병력·판정결과 | `output/<year>/p...json` (+`생년월일`은 `output_exposure_basic`에서 이동) |
| `exposure`   | 노출 물질 등 노출 기존값 | `output_exposure_basic/<year>/p...json` |
| `process`    | 생산품·작업도구·작업방식·작업공간·공정(+유해인자·고찰·결론) | `output_working/<year>/p...json` |

## 재생성
루트의 `build_json.py` 가 위 4개 소스를 fid 기준으로 병합해 이 폴더를 다시 만든다.
```
python3 build_json.py [<소스_base_dir>]
```

## 병합 규칙 · 알려진 특이사항
- **`process`(output_working)** 는 같은 fid 에 `*_sections.json` 과 기본 파일이 함께 있으면
  더 풍부한 **`*_sections.json` 을 우선** 채택한다.
- **`titles_pYYYY.json`** 등 fid 패턴이 아닌 집계 파일은 제외한다.
- **fid 충돌**: `kosha2009_095_096` 은 서로 다른 사례 2건이 같은 페이지 범위를 가져
  population/exposure 소스에 파일이 2개다. 현재는 파일명 정렬상 **첫 번째만** 채택한다.
- **`생년월일`** 은 원래 `output_exposure_basic` 에만 있으나 인적 특성이라
  **`population` 에 포함**시킨다(`질병확진나이` 뒤에 배치, 1579건). `exposure` 원본에도 그대로 남아 있다.
- **`exposure`** 는 아직 단위(mg 등)가 없는 기존값 상태이며, 상당수 레코드는 개인필드(나이/생년월일)만 담고 있다.
  추후 단위 포함 실제 노출값으로 확장 예정.
- **커버리지**: 소스마다 포함 fid 가 조금씩 달라, 전체는 **합집합(1664건)** 으로 생성한다.
  (summary 1627 · population 1594 · exposure 1601 · process 1632 — 2026-07-04 기준)
