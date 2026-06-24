from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = [
    "EMPLOYEE CODE",
    "EMPLOYEE NAME",
    "DATE",
    "TIME IN",
    "TIME OUT",
]


def load_dtr(input_path: Path) -> pd.DataFrame:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    df = pd.read_excel(input_path)
    df.columns = [str(column).strip().upper() for column in df.columns]

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    return df


def clean_raw_logs(df: pd.DataFrame) -> pd.DataFrame:
    raw = df.copy()

    raw["EMPLOYEE CODE"] = raw["EMPLOYEE CODE"].astype(str).str.strip()
    raw["EMPLOYEE NAME"] = raw["EMPLOYEE NAME"].astype(str).str.strip()
    raw["DATE"] = pd.to_datetime(raw["DATE"], errors="coerce").dt.date

    raw["TIME IN"] = pd.to_datetime(raw["TIME IN"], errors="coerce")
    raw["TIME OUT"] = pd.to_datetime(raw["TIME OUT"], errors="coerce")

    raw = raw.dropna(subset=["EMPLOYEE CODE", "DATE"])
    return raw


def normalize_time_in_out(raw: pd.DataFrame) -> pd.DataFrame:
    grouped = raw.groupby(["EMPLOYEE CODE", "EMPLOYEE NAME", "DATE"], dropna=False)

    summary = grouped.agg(
        FIRST_IN=("TIME IN", "min"),
        LAST_OUT=("TIME OUT", "max"),
        RAW_LOG_COUNT=("EMPLOYEE CODE", "count"),
    ).reset_index()

    summary = summary.sort_values(["EMPLOYEE CODE", "DATE"])

    summary["FIRST_IN"] = pd.to_datetime(summary["FIRST_IN"], errors="coerce")
    summary["LAST_OUT"] = pd.to_datetime(summary["LAST_OUT"], errors="coerce")

    summary["FIRST_IN_TIME"] = summary["FIRST_IN"].dt.strftime("%H:%M:%S")
    summary["LAST_OUT_TIME"] = summary["LAST_OUT"].dt.strftime("%H:%M:%S")

    export_columns = [
        "EMPLOYEE CODE",
        "EMPLOYEE NAME",
        "DATE",
        "FIRST_IN_TIME",
        "LAST_OUT_TIME",
        "RAW_LOG_COUNT",
    ]

    return summary[export_columns]


def export_cleaned_data(raw: pd.DataFrame, summary: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_export = raw.copy()
    raw_export["TIME IN"] = raw_export["TIME IN"].dt.strftime("%Y-%m-%d %H:%M:%S")
    raw_export["TIME OUT"] = raw_export["TIME OUT"].dt.strftime("%Y-%m-%d %H:%M:%S")

    raw_csv = output_dir / "raw_biometric_logs.csv"
    summary_csv = output_dir / "attendance_time_in_out.csv"
    summary_xlsx = output_dir / "attendance_time_in_out.xlsx"

    raw_export.to_csv(raw_csv, index=False)
    summary.to_csv(summary_csv, index=False)

    with pd.ExcelWriter(summary_xlsx, engine="openpyxl") as writer:
        summary.to_excel(writer, index=False, sheet_name="Time In Time Out")
        raw_export.to_excel(writer, index=False, sheet_name="Raw Logs")

    print("DTR processing complete.")
    print(f"Raw logs exported: {raw_csv}")
    print(f"Clean summary CSV exported: {summary_csv}")
    print(f"Clean summary Excel exported: {summary_xlsx}")
    print(f"Raw rows: {len(raw_export)}")
    print(f"Clean attendance rows: {len(summary)}")
    print(f"Employees: {summary['EMPLOYEE CODE'].nunique()}")


def process_dtr(input_path: Path, output_dir: Path) -> None:
    df = load_dtr(input_path)
    raw = clean_raw_logs(df)
    summary = normalize_time_in_out(raw)
    export_cleaned_data(raw, summary, output_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Process DTR into exportable Time In / Time Out attendance files.")
    parser.add_argument("input", help="Path to the DTR Excel file.")
    parser.add_argument("--output", default="exports", help="Output folder. Default: exports")
    args = parser.parse_args()

    process_dtr(Path(args.input), Path(args.output))


if __name__ == "__main__":
    main()
