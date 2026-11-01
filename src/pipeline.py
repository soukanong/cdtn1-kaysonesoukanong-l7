"""Điều phối bốn pha: extract -> transform -> quality -> load.  Chạy: python -m src.pipeline

Bốn quyết định thiết kế:
  1. Kiểm chất lượng chạy TRƯỚC khi nạp: quy tắc gate=true không đạt ở CLEAN thì DỪNG.
  2. Không nạp một phần: toàn bộ nạp kho nằm trong MỘT transaction.
  3. Báo cáo LUÔN được ghi (khối finally), kể cả khi thất bại.
  4. Mã thoát: 0 thành công · 1 lỗi kỹ thuật · 2 dừng vì chất lượng không đạt.
Tùy chọn --check-only: chỉ đọc, biến đổi và đo; KHÔNG kết nối CSDL.
"""
import argparse
import datetime as dt
import json
import logging
import os
import sys
import time

from src import config, db
from src.errors import SystemFault
from src.extract import read_source
from src.load import loader
from src.quality import checks
from src.transform import clean_customers

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"),
                    format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("pipeline")

EXIT_OK, EXIT_TECHNICAL, EXIT_QUALITY = 0, 1, 2


def write_report(report: dict) -> None:
    folder = config.report_dir()
    folder.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    (folder / f"chat-luong-{stamp}.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    lines = ["# Báo cáo chất lượng dữ liệu", "",
             f"- Kết luận: **{report['conclusion']}**",
             f"- Tệp nguồn: `{report.get('source_file', '')}`",
             f"- Thời gian chạy: {report.get('elapsed_seconds', 0)} giây", ""]
    if report.get("error"):
        lines += [f"- Lỗi: {report['error']}", ""]
    if report.get("stages"):
        lines += ["## Số dòng", ""] + [f"- {k}: {v}" for k, v in report["stages"].items()] + [""]
    if report.get("measures"):
        lines += ["## Phép đo chất lượng", "",
                  "| Quy tắc | Giai đoạn | Tổng | Vi phạm | Tỉ lệ đạt (%) | Ngưỡng (%) | Đạt |",
                  "|---|---|---:|---:|---:|---:|---|"]
        for m in report["measures"]:
            lines.append(f"| {m['rule_code']} | {m['stage']} | {m['total']} | {m['failed']} | "
                         f"{m['pass_rate_pct']} | {m['threshold_pct']} | "
                         f"{'ĐẠT' if m['is_threshold_met'] else '**KHÔNG ĐẠT**'} |")
        lines.append("")
    if report.get("reject_by_reason"):
        lines += ["## Bản ghi bị loại", ""] + [f"- {k}: {v}" for k, v in report["reject_by_reason"].items()]
    (folder / f"chat-luong-{stamp}.md").write_text("\n".join(lines), encoding="utf-8")


def run(check_only: bool = False) -> tuple[dict, int]:
    t0, started = time.perf_counter(), dt.datetime.now()
    report: dict = {"conclusion": "LOI", "started_at": started.isoformat(timespec="seconds")}
    code = EXIT_TECHNICAL
    raw_count, source = 0, ""
    try:
        rules_cfg = config.load_rules()
        path = config.source_csv()
        source = path.name
        report["source_file"] = source
        log.info("Đọc tệp nguồn: %s", path)

        raw = read_source.read_customers(path)                                  # PHA 1
        raw_count = len(raw)
        result = clean_customers.transform_customers(raw)                       # PHA 2
        measures = checks.measure_all(result, rules_cfg)                        # PHA 3
        issues = checks.collect_issues(result.raw)

        report["measures"] = [m.as_dict() for m in measures]
        report["clean_score"] = checks.clean_score(measures)
        report["reject_by_reason"] = result.rejects["reason_code"].value_counts().to_dict()
        report["stages"] = {"read": raw_count, "rejected": len(result.rejects),
                            "valid": result.valid_rows, "clean_unique": len(result.clean),
                            "attached_in_file": result.attached_in_file,
                            "suspect_groups": int(result.suspects["group_id"].nunique()),
                            "suspect_records": int(result.suspects["phone"].nunique())}

        failed = checks.gate_failures(measures, rules_cfg)
        if failed:
            for m in failed:
                log.error("%s KHÔNG ĐẠT ở CLEAN: %.2f%% < %.2f%%", m.rule_code, m.pass_rate_pct, m.threshold_pct)
            report["conclusion"] = "DUNG_VI_CHAT_LUONG"
            code = EXIT_QUALITY
            return report, code
        if check_only:
            report["conclusion"] = "CHI_KIEM_KHONG_NAP"
            code = EXIT_OK
            return report, code

        engine = db.get_engine()                                                # PHA 4
        db.apply_schema(engine)
        info = loader.load_run(engine, result, measures, issues, rules_cfg, source, started)
        report["stages"].update({k: v for k, v in info.items() if k != "table_counts"})
        report["table_counts"] = info["table_counts"]
        report["conclusion"] = "THANH_CONG"
        code = EXIT_OK
        return report, code
    except SystemFault as e:
        log.error("Lỗi kỹ thuật: %s", e)
        report["error"] = str(e)
        return report, EXIT_TECHNICAL
    except Exception as e:                                                      # noqa: BLE001
        log.exception("Pipeline thất bại")
        report["error"] = type(e).__name__                  # không đưa chuỗi kết nối vào báo cáo
        if not check_only:
            try:
                loader.record_failed_run(db.get_engine(), source, raw_count, started)
            except Exception:                               # noqa: BLE001
                pass
        return report, EXIT_TECHNICAL
    finally:
        report["elapsed_seconds"] = round(time.perf_counter() - t0, 2)
        try:
            write_report(report)
        except Exception:                                                       # noqa: BLE001
            log.exception("Không ghi được báo cáo")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Pipeline làm sạch dữ liệu khách hàng L7")
    ap.add_argument("--check-only", action="store_true", help="Chỉ đọc, biến đổi, đo. Không nạp CSDL.")
    args = ap.parse_args(argv)
    report, code = run(check_only=args.check_only)
    s = report.get("stages", {})
    print(f"Kết luận: {report['conclusion']} (mã thoát {code}) | {report.get('elapsed_seconds')} giây")
    if s:
        print(f"Đọc {s.get('read')} | loại {s.get('rejected')} {report.get('reject_by_reason', {})} | "
              f"sạch {s.get('clean_unique')} | nghi trùng {s.get('suspect_groups')} nhóm")
    if "clean_score" in report:
        print(f"Điểm sạch (CLEAN): {report['clean_score']}")
    if report.get("error"):
        print(f"Lỗi: {report['error']}")
    return code


if __name__ == "__main__":
    sys.exit(main())
