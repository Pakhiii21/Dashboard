import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Lab Parameter Violation Dashboard", layout="wide")

st.title("🧪 Lab Quality Parameter Violation Dashboard")
st.markdown("Upload an Excel file to visualize and flag samples that **violate JFS specs** for selected parameters (1, 2, 6, 7).")

uploaded_file = st.file_uploader("📤 Upload Excel File", type=["xlsx"])

def find_column(columns, keywords):
    for col in columns:
        for kw in keywords:
            if kw in str(col).lower():
                return col
    return None

if uploaded_file:
    excel = pd.ExcelFile(uploaded_file)
    sheet_names = excel.sheet_names
    st.success(f"Loaded {len(sheet_names)} sheets: {sheet_names}")

    all_flagged_rows = []
    summary_dict = {}

    PARAM_SPECS = {
        "Moisture %": (8.0, 14.0),
        "Alcoholic Acidity %": (0.01, 0.12),
        "WAP": (60.5, 65.0),
        "Peak Time": (6.0, 8.0)
    }

    for sheet in sheet_names:
        raw_df = excel.parse(sheet, header=None)
        raw_df.dropna(how='all', inplace=True)

        header_row_idx = raw_df[raw_df.astype(str).apply(lambda row: row.str.contains("Supplier|Moisture", case=False, na=False).any(), axis=1)].index.min()

        if pd.isna(header_row_idx):
            st.warning(f"⚠️ Could not detect valid header in sheet '{sheet}'. Skipping.")
            continue

        df = excel.parse(sheet, skiprows=header_row_idx + 1)
        df.columns = raw_df.iloc[header_row_idx]
        df.dropna(how='all', inplace=True)

        # Identify key columns
        col_supplier = find_column(df.columns, ["supplier", "vendor", "name"])
        col_mfd = find_column(df.columns, ["mfd", "date", "manufacture"])
        col_moisture = find_column(df.columns, ["moisture"])
        col_acidity = find_column(df.columns, ["alcohol", "acidity"])
        col_wap = find_column(df.columns, ["wap"])
        col_peak = find_column(df.columns, ["peak", "time"])

        # Rename for consistency
        rename_map = {}
        if col_supplier: rename_map[col_supplier] = "Supplier"
        if col_mfd: rename_map[col_mfd] = "MFD"
        if col_moisture: rename_map[col_moisture] = "Moisture %"
        if col_acidity: rename_map[col_acidity] = "Alcoholic Acidity %"
        if col_wap: rename_map[col_wap] = "WAP"
        if col_peak: rename_map[col_peak] = "Peak Time"
        df.rename(columns=rename_map, inplace=True)

        for col in PARAM_SPECS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        if "MFD" in df.columns:
            df["MFD"] = pd.to_datetime(df["MFD"], errors='coerce')

        df["Sheet"] = sheet

        conditions = []
        for col, (low, high) in PARAM_SPECS.items():
            if col in df.columns:
                conditions.append(~df[col].between(low, high))

        if conditions:
            combined_condition = conditions[0]
            for cond in conditions[1:]:
                combined_condition |= cond
            flagged_df = df[combined_condition]
        else:
            flagged_df = pd.DataFrame()

        if not flagged_df.empty and "Supplier" in flagged_df.columns:
            all_flagged_rows.append(flagged_df)
            vendor_counts = flagged_df["Supplier"].value_counts().to_dict()
            for vendor, count in vendor_counts.items():
                summary_dict[vendor] = summary_dict.get(vendor, 0) + count
        else:
            st.info(f"ℹ️ No violations detected or 'Supplier' column missing in sheet '{sheet}'.")

    if all_flagged_rows:
        combined_flagged = pd.concat(all_flagged_rows, ignore_index=True)

        st.markdown(f"🔔 **{len(combined_flagged)} samples have parameter violations.**")
        st.dataframe(combined_flagged)

        if "Supplier" in combined_flagged.columns:
            st.markdown("### 🚩 Vendors with Violations:")
            vendor_summary = pd.DataFrame(list(summary_dict.items()), columns=["Vendor", "Violation Count"])
            vendor_summary = vendor_summary.sort_values(by="Violation Count", ascending=False)
            st.dataframe(vendor_summary)
        else:
            st.warning("⚠️ Could not create vendor summary — 'Supplier' column missing.")

        # 📊 Charts for each parameter
        st.markdown("### 📊 Violation Charts")
        for col in PARAM_SPECS:
            if col in combined_flagged.columns:
                chart = alt.Chart(combined_flagged.dropna(subset=[col])).mark_bar().encode(
                    x=alt.X('Supplier:N', sort='-y'),
                    y=alt.Y(f"{col}:Q"),
                    color=alt.value("orange"),
                    tooltip=["Supplier", col]
                ).properties(
                    width=600,
                    height=300,
                    title=f"{col} Violations by Supplier"
                )
                st.altair_chart(chart)

        # ⬇️ Download button
        def to_excel_bytes(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Flagged Samples")
                if summary_dict:
                    vendor_summary.to_excel(writer, index=False, sheet_name="Vendor Summary")
            return output.getvalue()

        st.download_button(
            label="⬇️ Download Flagged Data",
            data=to_excel_bytes(combined_flagged),
            file_name="Flagged_Parameters_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.success("✅ No violations found or no valid data in any sheet.")
