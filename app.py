from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from src.attendance.process_dtr import clean_raw_logs, load_dtr, normalize_time_in_out

UPLOAD_DIR = Path("imports")
EXPORT_DIR = Path("exports")

st.set_page_config(page_title="EWHC Payroll DTR Portal", page_icon="🕒", layout="wide")

st.title("EWHC Payroll DTR Upload Portal")
st.caption("Upload biometric DTR files and extract clean Time In / Time Out attendance data.")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

uploaded_file = st.file_uploader("Upload DTR Excel file", type=["xlsx", "xls"])

if uploaded_file is None:
    st.info("Upload a DTR Excel file to begin. The system will clean it using First In / Last Out rules.")
    st.stop()

safe_name = uploaded_file.name.replace(" ", "_")
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
input_path = UPLOAD_DIR / f"{timestamp}_{safe_name}"

with open(input_path, "wb") as file:
    file.write(uploaded_file.getbuffer())

try:
    df = load_dtr(input_path)
    raw = clean_raw_logs(df)
    summary = normalize_time_in_out(raw)
except Exception as exc:
    st.error(f"Unable to process file: {exc}")
    st.stop()

raw_export = raw.copy()
raw_export["TIME IN"] = raw_export["TIME IN"].dt.strftime("%Y-%m-%d %H:%M:%S")
raw_export["TIME OUT"] = raw_export["TIME OUT"].dt.strftime("%Y-%m-%d %H:%M:%S")

base_output_name = f"attendance_time_in_out_{timestamp}"
summary_csv_path = EXPORT_DIR / f"{base_output_name}.csv"
summary_xlsx_path = EXPORT_DIR / f"{base_output_name}.xlsx"
raw_csv_path = EXPORT_DIR / f"raw_biometric_logs_{timestamp}.csv"

summary.to_csv(summary_csv_path, index=False)
raw_export.to_csv(raw_csv_path, index=False)

with pd.ExcelWriter(summary_xlsx_path, engine="openpyxl") as writer:
    summary.to_excel(writer, index=False, sheet_name="Time In Time Out")
    raw_export.to_excel(writer, index=False, sheet_name="Raw Logs")

st.success("DTR processed successfully.")

col1, col2, col3 = st.columns(3)
col1.metric("Raw logs", f"{len(raw_export):,}")
col2.metric("Clean attendance rows", f"{len(summary):,}")
col3.metric("Employees", f"{summary['EMPLOYEE CODE'].nunique():,}")

st.subheader("Basic log chart")
chart_data = (
    summary.groupby("DATE", as_index=False)["RAW_LOG_COUNT"]
    .sum()
    .rename(columns={"DATE": "Date", "RAW_LOG_COUNT": "Raw log count"})
)
st.bar_chart(chart_data, x="Date", y="Raw log count")

st.subheader("Clean Time In / Time Out Preview")
st.dataframe(summary, use_container_width=True)

st.subheader("Download Extracted Files")

with open(summary_xlsx_path, "rb") as file:
    st.download_button(
        "Download cleaned Excel",
        file,
        file_name=summary_xlsx_path.name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

with open(summary_csv_path, "rb") as file:
    st.download_button(
        "Download cleaned CSV",
        file,
        file_name=summary_csv_path.name,
        mime="text/csv",
    )

with open(raw_csv_path, "rb") as file:
    st.download_button(
        "Download raw logs CSV",
        file,
        file_name=raw_csv_path.name,
        mime="text/csv",
    )
