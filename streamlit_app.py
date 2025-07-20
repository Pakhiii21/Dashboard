import streamlit as st
import pandas as pd

# Title
st.markdown("<h2 style='color:#2c3e50;'>🔬 Flour Quality Analysis Dashboard</h2>", unsafe_allow_html=True)

# Upload Excel file
uploaded_file = st.file_uploader("Upload lab Excel file", type=[".xlsx"])

if uploaded_file:
    excel = pd.ExcelFile(uploaded_file)

    # Define parameter rules (manual ranges)
    limits = {
        "Moisture %": (0.08, 0.14),
        "Alcoholic Acidity %": (0.01, 0.12),
        "Dry Gluten %": (0.105, 0.12),
        "Gluten Index %": (0.90, None),  # Min only
        "Total Ash %": (None, 0.0056),   # Max only
        "WAP": (0.605, 0.65),
        "Peak Time": (6, 8),
        "Stability": (12, 18),
        "MTI": (20, 40),
        "TPS": (38, 100),  # Example range for Pizza Sauce TPS
        "DRC": (38, None)   # Min only
    }

    def check_limits(row, limits):
        issues = []
        for col, (low, high) in limits.items():
            if col not in row:
                continue
            val = row[col]
            if pd.isna(val):
                continue
            if (low is not None and val < low) or (high is not None and val > high):
                issues.append(col)
        return ", ".join(issues) if issues else "OK"

    # Parse sheets and show flagged data
    for sheet in excel.sheet_names:
        try:
            df = excel.parse(sheet, skiprows=4)
            df.columns = df.columns[:2].tolist() + [str(c) for c in df.columns[2:]]
            df = df.rename(columns={
                df.columns[0]: "Supplier",
                df.columns[1]: "MFD",
                "8% to 14%": "Moisture %",
                "0.01 - 0.12 %": "Alcoholic Acidity %",
                "10.5 % to 12%": "Dry Gluten %",
                "Min. 90%": "Gluten Index %",
                "Max 0.56%": "Total Ash %",
                "Min 60.5%-65%": "WAP",
                "6-8 minutes": "Peak Time",
                "12-18 minutes": "Stability",
                "20-40 BU": "MTI"
            })

            for col in df.columns:
                if col in limits:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            df["Out of Spec"] = df.apply(lambda row: check_limits(row, limits), axis=1)

            outliers = df[df["Out of Spec"] != "OK"]

            st.markdown(f"### 📄 Sheet: {sheet}")
            if not outliers.empty:
                st.warning(f"🚨 {len(outliers)} samples have parameter violations.")
                st.dataframe(outliers)
            else:
                st.success("✅ All samples meet standard parameters.")
        except Exception as e:
            st.error(f"Error processing sheet '{sheet}': {e}")

    st.markdown("---")
    st.caption("Lab Quality Flagging Dashboard | Developed by QA Team")
