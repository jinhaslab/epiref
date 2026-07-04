#!/usr/bin/env python3
"""epiref docs/*_population.html, *_process.html 에서 구조화 정보를 뽑아
docs/json/<fid>.json 으로 저장한다.

사용법:
  python3 build_json.py <fid>     # 한 건만 (예: kosha2000_003_004)
  python3 build_json.py --all     # 전체
"""
import sys
import os
import re
import json
import html as htmllib
from html.parser import HTMLParser

DOCS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
JSON_DIR = os.path.join(DOCS, "json")

SECTIONS = ("population", "process", "exposure")  # exposure는 향후 대비


class TableParser(HTMLParser):
    """구분/내용 2열 테이블을 {구분: [값,...]} 으로 파싱.
    rowspan 으로 병합된 key 는 여러 값을 리스트로 모은다."""

    def __init__(self):
        super().__init__()
        self.in_tbody = False
        self.in_td = False
        self.cur_text = []
        self.row_cells = []  # 현재 <tr> 안의 td 텍스트들
        self.result = {}     # 순서 유지 dict
        self.cur_key = None

    def handle_starttag(self, tag, attrs):
        if tag == "tbody":
            self.in_tbody = True
        elif tag == "tr" and self.in_tbody:
            self.row_cells = []
        elif tag == "td" and self.in_tbody:
            self.in_td = True
            self.cur_text = []

    def handle_endtag(self, tag):
        if tag == "tbody":
            self.in_tbody = False
        elif tag == "td" and self.in_td:
            self.in_td = False
            self.row_cells.append("".join(self.cur_text).strip())
        elif tag == "tr" and self.in_tbody:
            if len(self.row_cells) >= 2:
                # 새 key + 첫 값
                key, val = self.row_cells[0], self.row_cells[1]
                self.cur_key = key
                self.result.setdefault(key, []).append(val)
            elif len(self.row_cells) == 1 and self.cur_key is not None:
                # rowspan 이어지는 값
                self.result[self.cur_key].append(self.row_cells[0])
            self.row_cells = []

    def handle_data(self, data):
        if self.in_td:
            self.cur_text.append(data)


def parse_section(path):
    with open(path, encoding="utf-8") as f:
        p = TableParser()
        p.feed(f.read())
    # 빈 문자열 값 정리
    return {k: [htmllib.unescape(v) for v in vs if v != ""] for k, vs in p.result.items()}


def build_one(fid):
    record = {"fid": fid}
    m = re.match(r"kosha(\d{4})_", fid)
    if m:
        record["year"] = int(m.group(1))
    found = False
    for sec in SECTIONS:
        path = os.path.join(DOCS, f"{fid}_{sec}.html")
        if os.path.exists(path):
            record[sec] = parse_section(path)
            found = True
    if not found:
        return None
    return record


def all_fids():
    fids = set()
    for name in os.listdir(DOCS):
        m = re.match(r"(kosha\d{4}_\d+_\d+)_(population|process|exposure)\.html$", name)
        if m:
            fids.add(m.group(1))
    return sorted(fids)


def write_json(record):
    os.makedirs(JSON_DIR, exist_ok=True)
    out = os.path.join(JSON_DIR, f"{record['fid']}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    return out


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    if argv[1] == "--all":
        fids = all_fids()
        n = 0
        for fid in fids:
            rec = build_one(fid)
            if rec:
                write_json(rec)
                n += 1
        print(f"{n}/{len(fids)} JSON 생성 → {JSON_DIR}")
    else:
        fid = argv[1]
        rec = build_one(fid)
        if rec is None:
            print(f"해당 fid 의 html 이 없습니다: {fid}")
            return 1
        # 미리보기: 파일로 저장하고 내용도 출력
        out = write_json(rec)
        print(f"저장: {out}\n")
        print(json.dumps(rec, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
