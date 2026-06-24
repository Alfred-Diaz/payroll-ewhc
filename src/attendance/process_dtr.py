from __future__ import annotations

import argparse
from datetime import datetime, time, timedelta
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = ["EMPLOYEE CODE", "EMPLOYEE NAME", "DATE", "TIME IN", "TIME OUT"]


def load_dtr(input_path: Path) -> pd.DataFrame:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    df = pd.read_excel(input_path)
    df.columns = [str(column).strip().upper() for column in df.columns]
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df


def parse_dtr_datetime(date_value, time_value):
    if pd.isna(date_value) or pd.isna(time_value):
        return pd.NaT

    date_part = pd.to_datetime(date_value, errors="coerce")
    if pd.isna(date_part):
        return pd.NaT
    date_part = date_part.date()

    if isinstance(time_value, time):
        time_part = time_value
    elif isinstance(time_value, datetime):
        time_part = time_value.time()
    elif isinstance(time_value, pd.Timestamp):
        time_part = time_value.time()
    elif isinstance(time_value, (int, float)):
        seconds = round(float(time_value) * 86400) % 86400
        time_part = (datetime.min + timedelta(seconds=seconds)).time()
    else:
        text_value = str(time_value).strip()
        if text_value.lower() in {"", "nan", "nat", "none", "null"}:
            return pd.NaT
        parsed_time = pd.to_datetime(text_value, errors="coerce")
        if pd.isna(parsed_time):
            return pd.NaT
        time_part = parsed_time.time()

    return pd.Timestamp(datetime.combine(date_part, time_part))


def clean_raw_logs(df: pd.DataFrame) -> pd.DataFrame:
    raw = df.copy()
    raw["EMPLOYEE CODE"] = raw["EMPLOYEE CODE"].astype(str).str.strip()
    raw["EMPLOYEE NAME"] = raw["EMPLOYEE NAME"].astype(str).str.strip()
    raw["DATE"] = pd.to_datetime(raw["DATE"], errors="coerce").dt.date

    original_dates = df["DATE"]
    raw["TIME IN"] = [parse_dtr_datetime(date_value, time_value) for date_value, time_value in zip(original_dates, df["TIME IN"])]
    raw["TIME OUT"] = [parse_dtr_datetime(date_value, time_value) for date_value, time_value in zip(original_dates, df["TIME OUT"])]

    return raw.dropna(subset=["EMPLOYEE CODE", "DATE"])


def build_punch_logs(raw: pd.DataFrame) -> pd.DataFrame:
    id_cols = ["EMPLOYEE CODE", "EMPLOYEE NAME", "DATE"]
    in_rows = raw[id_cols + ["TIME IN"]].rename(columns={"TIME IN": "PUNCH_TIME"})
    in_rows["PUNCH_SOURCE"] = "TIME IN"
    out_rows = raw[id_cols + ["TIME OUT"]].rename(columns={"TIME OUT": "PUNCH_TIME"})
    out_rows["PUNCH_SOURCE"] = "TIME OUT"
    punches = pd.concat([in_rows, out_rows], ignore_index=True)
    punches = punches.dropna(subset=["PUNCH_TIME"])
    return punches.sort_values(["EMPLOYEE CODE", "DATE", "PUNCH_TIME"])


def minutes_to_hhmm(minutes_value) -> str:
    if pd.isna(minutes_value):
        return ""
    minutes_value = int(minutes_value)
    return f"{minutes_value // 60:02d}:{minutes_value % 60:02d}"


def normalize_time_in_out(raw: pd.DataFrame) -> pd.DataFrame:
    punches = build_punch_logs(raw)
    keys = ["EMPLOYEE CODE", "EMPLOYEE NAME", "DATE"]

    summary = punches.groupby(keys, dropna=False).agg(
        FIRST_IN=("PUNCH_TIME", "min"),
        LAST_OUT=("PUNCH_TIME", "max"),
        VALID_PUNCH_COUNT=("PUNCH_TIME", "count"),
    ).reset_index()

    raw_counts = raw.groupby(keys, dropna=False).size().reset_index(name="RAW_ROW_COUNT")
    summary = summary.merge(raw_counts, on=keys, how="left")
    summary = summary.sort_values(["EMPLOYEE CODE", "DATE"])

    summary["FIRST_IN"] = pd.to_datetime(summary["FIRST_IN"], errors="coerce")
    summary["LAST_OUT"] = pd.to_datetime(summary["LAST_OUT"], errors="coerce")
    summary["FIRST_IN_TIME"] = summary["FIRST_IN"].dt.strftime("%H:%M:%S")
    summary["LAST_OUT_TIME"] = summary["LAST_OUT"].dt.strftime("%H:%M:%S")

    summary["DURATION_MINUTES"] = ((summary["LAST_OUT"] - summary["FIRST_IN"]).dt.total_seconds() / 60).round()
    summary.loc[summary["DURATION_MINUTES"] < 0, "DURATION_MINUTES"] = pd.NA
    summary["DURATION_MINUTES"] = summary["DURATION_MINUTES"].astype("Int64")
    summary["DURATION_HOURS"] = (summary["DURATION_MINUTES"] / 60).round(2)
    summary["DURATION_HHMM"] = summary["DURATION_MINUTES"].apply(minutes_to_hhmm)
    summary["HAS_MISSING_TIME"] = summary["FIRST_IN_TIME"].isna() | summary["LAST_OUT_TIME"].isna()

    return summary[[
        "EMPLOYEE CODE", "EMPLOYEE NAME", "DATE",
        "FIRST_IN_TIME", "LAST_OUT_TIME",
        "DURATION_HHMM", "DURATION_HOURS", "DURATION_MINUTES",
        "VALID_PUNCH_COUNT", "RAW_ROW_COUNT", "HAS_MISSING_TIME",
    ]]


def export_cleaned_data(raw: pd.DataFrame, summary: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_export = raw.copy()
    raw_export["TIME IN"] = raw_export["TIME IN"].dt.strftime("%Y-%m-%d %H:%M:%S")
    raw_export["TIME OUT"] = raw_export["TIME OUT"].dt.strftime("%Y-%m-%d %H:%M:%S")

    punches_export = build_punch_logs(raw).copy()
    punches_export["PUNCH_TIME"] = punches_export["PUNCH_TIME"].dt.strftime("%Y-%m-%d %H:%M:%S")

    raw_csv = output_dir / "raw_biometric_logs.csv"
    punches_csv = output_dir / "normalized_punch_logs.csv"
    summary_csv = output_dir / "attendance_time_in_out.csv"
    summary_xlsx = output_dir / "attendance_time_in_out.xlsx"

    raw_export.to_csv(raw_csv, index=False)
    punches_export.to_csv(punches_csv, index=False)
    summary.to_csv(summary_csv, index=False)

    with pd.ExcelWriter(summary_xlsx, engine="openpyxl") as writer:
        summary.to_excel(writer, index=False, sheet_name="Time In Time Out")
        punches_export.to_excel(writer, index=False, sheet_name="Punch Logs")
        raw_export.to_excel(writer, index=False, sheet_name="Raw Logs")

    print("DTR processing complete.")
    print(f"Raw logs exported: {raw_csv}")
    print(f"Normalized punch logs exported: {punches_csv}")
    print(f"Clean summary CSV exported: {summary_csv}")
    print(f"Clean summary Excel exported: {summary_xlsx}")
    print(f"Raw rows: {len(raw_export)}")
    print(f"Valid punches: {len(punches_export)}")
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
