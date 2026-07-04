#!/usr/bin/env python3
"""ote 파이프라인이 미리 추출한 JSON 4종을 fid(파일명) 기준으로 병합해
epiref/docs/json/<fid>.json 단일 파일로 저장한다.

소스(기본값: scratchpad 스테이징 폴더):
  kosha_final/<fid>.json                  -> summary   (메인 요약)
  output/<year>/p..._제목.json            -> population(개인특성/노출인자)
  output_exposure_basic/<year>/p...json   -> exposure  (노출 기존값, 단위 미포함)
  output_working/<year>/p...json          -> process   (공정; *_sections.json 우선)

공통키(foreign key)는 fid = koshaYYYY_PPP_QQQ (=파일명).

사용법:
  python3 build_json.py            # 기본 소스에서 전체 생성
  python3 build_json.py <소스base> # 소스 base 지정
"""
import os
import re
import sys
import json
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "docs", "json")
DEFAULT_SRC = ("/private/tmp/claude-502/-Users-kosha-kosha-server/"
               "d5943573-6235-473a-a1ca-99429e3407f2/scratchpad/ote_stage")

PDIR_FID = re.compile(r"^p(\d{4})_(\d+)_(\d+)_")          # output* 파일명 -> fid
PDIR_TITLE = re.compile(r"^p\d{4}_\d+_\d+_[^_]*_\d+_(.*)\.json$")  # 제목 추출


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def fid_of(fn):
    m = PDIR_FID.match(fn)
    return f"kosha{m.group(1)}_{m.group(2)}_{m.group(3)}" if m else None


def index_pdir(root, prefer_sections=False):
    """output* 디렉토리를 {fid: (path, filename)} 로 인덱싱.
    prefer_sections=True 면 같은 fid 에 *_sections.json 을 우선 채택.
    titles_*.json 같은 비-fid 파일은 제외. 반환: (index, dup_fids)."""
    cand = collections.defaultdict(list)
    for dp, _, files in os.walk(root):
        for fn in files:
            if not fn.endswith(".json"):
                continue
            fid = fid_of(fn)
            if not fid:                       # titles_pYYYY.json 등 제외
                continue
            cand[fid].append(os.path.join(dp, fn))
    index, dups = {}, []
    for fid, paths in cand.items():
        if len(paths) > 1:
            dups.append((fid, [os.path.basename(p) for p in paths]))
        if prefer_sections:
            sec = [p for p in paths if p.endswith("_sections.json")]
            paths = sec or paths
        index[fid] = sorted(paths)[0]         # 결정적으로 첫 번째 채택
    return index, dups


def title_from_filename(path):
    m = PDIR_TITLE.match(os.path.basename(path))
    return m.group(1).strip() if m else None


def main(argv):
    src = argv[1] if len(argv) > 1 else DEFAULT_SRC
    final_dir = os.path.join(src, "kosha_final")

    final = {f[:-5]: os.path.join(final_dir, f)
             for f in os.listdir(final_dir) if f.endswith(".json")}
    pop, pop_dup = index_pdir(os.path.join(src, "output"))
    exp, exp_dup = index_pdir(os.path.join(src, "output_exposure_basic"))
    prc, prc_dup = index_pdir(os.path.join(src, "output_working"), prefer_sections=True)

    all_fids = sorted(set(final) | set(pop) | set(exp) | set(prc))

    os.makedirs(OUT_DIR, exist_ok=True)
    counts = collections.Counter()
    for fid in all_fids:
        m = re.match(r"kosha(\d{4})_(\d+_\d+)$", fid)
        rec = {"fid": fid}
        if m:
            rec["year"] = int(m.group(1))
            rec["page"] = m.group(2)
        title = None
        if fid in final:
            s = load(final[fid])
            title = s.get("제목")
            # 중복 메타는 최상위로 승격하고 summary 에서는 제거
            for k in ("년도", "페이지", "파일명"):
                s.pop(k, None)
            rec["summary"] = s
            counts["summary"] += 1
        exp_data = load(exp[fid]) if fid in exp else None
        if fid in pop:
            population = load(pop[fid])
            # 생년월일은 원래 exposure(output_exposure_basic)에만 있으나
            # 인적 특성이라 population 에 포함시킨다(질병확진나이 뒤에 배치).
            if exp_data and "생년월일" not in population and exp_data.get("생년월일"):
                ordered_pop = {}
                for k, v in population.items():
                    ordered_pop[k] = v
                    if k == "질병확진나이":
                        ordered_pop["생년월일"] = exp_data["생년월일"]
                if "생년월일" not in ordered_pop:      # 질병확진나이가 없으면 맨 뒤
                    ordered_pop["생년월일"] = exp_data["생년월일"]
                population = ordered_pop
                counts["생년월일_주입"] += 1
            rec["population"] = population
            title = title or title_from_filename(pop[fid])
            counts["population"] += 1
        if exp_data is not None:
            rec["exposure"] = exp_data
            counts["exposure"] += 1
        if fid in prc:
            rec["process"] = load(prc[fid])
            title = title or title_from_filename(prc[fid])
            counts["process"] += 1
        if title:
            rec["title"] = title
        # title 을 fid 다음 위치로 정렬해 가독성 확보
        ordered = {}
        for k in ("fid", "year", "page", "title",
                  "summary", "population", "exposure", "process"):
            if k in rec:
                ordered[k] = rec[k]
        with open(os.path.join(OUT_DIR, f"{fid}.json"), "w", encoding="utf-8") as f:
            json.dump(ordered, f, ensure_ascii=False, indent=2)
        counts["files"] += 1

    print(f"생성 파일: {counts['files']}  ->  {OUT_DIR}")
    print(f"  섹션 포함수: summary={counts['summary']} population={counts['population']} "
          f"exposure={counts['exposure']} process={counts['process']}")
    print(f"  전체 fid(합집합): {len(all_fids)}")
    for name, dup in (("output", pop_dup), ("exposure_basic", exp_dup),
                      ("working", prc_dup)):
        if dup:
            print(f"  [중복 fid] {name}: {len(dup)}건 (첫 파일 채택)")
            for fid, files in dup[:3]:
                print(f"      {fid}: {files}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
