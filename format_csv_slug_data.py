"""
Format slug test CSV results into a summary Excel file.

Reads estimated_conductivity.csv from both Butler and Bouwer-Rice output
folders, joins with the batch metadata to obtain well names and test dates,
converts K from ft/sec to ft/day, and writes a formatted Excel workbook
with one sheet per analysis method.
"""

import re
import pandas as pd
import numpy as np

FT_SEC_TO_FT_DAY = 86400

CSV_FILES = {
    "Butler": r"C:\workspace\projects\pump_tests\WRD_Slug_Data\output_butler\estimated_conductivity.csv",
    "Bouwer_Rice": r"C:\workspace\projects\pump_tests\WRD_Slug_Data\output_Bouwer_Rice\estimated_conductivity.csv",
}
BATCH_FILE = r"C:\workspace\projects\pump_tests\WRD_Slug_Data\wrd_batch_data_clean_Bouwer_Rice.csv"
OUTPUT_EXCEL = r"C:\workspace\projects\pump_tests\WRD_Slug_Data\slug_test_summary.xlsx"


def load_batch_info(batch_file: str) -> dict:
    """Build a lookup: test_id -> {well_name, test_date}."""
    df = pd.read_csv(batch_file)
    df = df.set_index("field").transpose()

    info = {}
    for _, row in df.iterrows():
        tid = row.get("test_id")
        if pd.isna(tid):
            continue
        tid = str(tid).strip()
        well_name = str(row.get("well_name", "")).strip()
        raw_date = row.get("Test Date", "")
        try:
            dt = pd.to_datetime(raw_date)
            test_date = dt.strftime("%m/%d/%Y")
        except Exception:
            test_date = str(raw_date)
        info[tid] = {"well_name": well_name, "test_date": test_date}
    return info


def parse_test_name(name: str):
    """Split 'LB6_1_T2' into ('LB6_1', 'T2')."""
    match = re.match(r"(.+)_(T\d+)$", name)
    if match:
        return match.group(1), match.group(2)
    return name, None


def build_summary(csv_file: str, batch_info: dict) -> pd.DataFrame:
    """Create the per-well summary table from one estimated_conductivity CSV."""
    df = pd.read_csv(csv_file)

    parsed = df["test_name"].apply(lambda n: pd.Series(parse_test_name(n)))
    df["well_code"] = parsed[0]
    df["test_num"] = parsed[1]
    df["K_ft_day"] = df["hydraulic_conductivity"] * FT_SEC_TO_FT_DAY

    rows = []
    for well_code, grp in df.groupby("well_code", sort=False):
        first_tid = grp["test_name"].iloc[0]
        meta = batch_info.get(first_tid, {})
        well_name = meta.get("well_name", well_code)
        test_date = meta.get("test_date", "")

        k_by_test = {r["test_num"]: r["K_ft_day"] for _, r in grp.iterrows()}
        t1 = k_by_test.get("T1")
        t2 = k_by_test.get("T2")
        t3 = k_by_test.get("T3")

        vals = [v for v in (t1, t2, t3) if v is not None]
        avg_k = np.mean(vals) if vals else None
        std_k = np.std(vals) if len(vals) > 1 else 0.0

        rows.append(
            {
                "Well Casing ID": well_code,
                "Slug Test Date": test_date,
                "Slug Test 1 (T1)": round(t1, 2) if t1 is not None else None,
                "Slug Test 2 (T2)": round(t2, 2) if t2 is not None else None,
                "Slug Test 3 (T3)": round(t3, 2) if t3 is not None else None,
                "Average K": round(avg_k, 2) if avg_k is not None else None,
                "Standard Deviation K": round(std_k, 2) if std_k is not None else None,
            }
        )

    return pd.DataFrame(rows)


def format_sheet(ws):
    """Apply basic formatting: bold header, auto-fit column widths."""
    from openpyxl.styles import Font, Alignment

    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center", wrap_text=True)

    for col in ws.columns:
        max_len = 0
        col_letter = col[0].column_letter
        for cell in col:
            val = str(cell.value) if cell.value is not None else ""
            max_len = max(max_len, len(val))
        ws.column_dimensions[col_letter].width = min(max_len + 4, 30)


def main():
    batch_info = load_batch_info(BATCH_FILE)

    with pd.ExcelWriter(OUTPUT_EXCEL, engine="openpyxl") as writer:
        for method, csv_path in CSV_FILES.items():
            df_summary = build_summary(csv_path, batch_info)
            df_summary.to_excel(writer, sheet_name=method, index=False)
            format_sheet(writer.sheets[method])

    print(f"Summary written to {OUTPUT_EXCEL}")


if __name__ == "__main__":
    main()
