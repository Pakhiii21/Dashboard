import streamlit as st
import pandas as pd
import altair as alt

# Page setup
st.set_page_config(page_title="Weekly Lab Analysis", layout="wide")
st.markdown("<h1 style='color:#2c3e50;'>📊 Weekly Lab Analysis</h1>", unsafe_allow_html=True)

# Upload Excel
uploaded_file = st.file_uploader("📁 Upload lab Excel file", type=[".xlsx"])

# Define parameter rules (parameters 1, 2, 6, 7 only)
limits = {
    "Moisture %": (0.08, 0.14),                # 1
    "Alcoholic Acidity %": (0.01, 0.12),       # 2
    "WAP": (0.605, 0.65),                      # 6
    "Peak Time": (6, 8),                       # 7
}

# Check if value is within spec
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

if uploaded_file:
    excel = pd.ExcelFile(uploaded_file)

    for sheet in excel.sheet_names:
        try:
            df = excel.parse(sheet, skiprows=4)

            # Fix headers
            df.columns = df.columns[:2].tolist() + [str(c) for c in df.columns[2:]]
            df = df.rename(columns={
                df.columns[0]: "Supplier",
                df.columns[1]: "MFD",
                "8% to 14%": "Moisture %",
                "0.01 - 0.12 %": "Alcoholic Acidity %",
                "Min 60.5%-65%": "WAP",
                "6-8 minutes": "Peak Time"
            })

            # Convert numeric columns
            for col in limits:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # Flag out-of-spec rows
            df["Out of Spec"] = df.apply(lambda row: check_limits(row, limits), axis=1)

            # Replace None/NaN with empty string for display
            df.fillna("", inplace=True)

            st.markdown(f"### 📄 Sheet: `{sheet}`")
            search_text = st.text_input(f"🔍 Search in `{sheet}`", "")

            if search_text:
                mask = df.apply(lambda row: row.astype(str).str.contains(search_text, case=False, na=False).any(), axis=1)
                filtered = df[mask]
            else:
                filtered = df.copy()

            # Show filtered full sheet
            st.dataframe(filtered, use_container_width=True)

            # Show violations if any
            outliers = filtered[filtered["Out of Spec"] != "OK"]

            if not outliers.empty:
                st.warning(f"🚨 {len(outliers)} samples have parameter violations.")
                st.dataframe(outliers, use_container_width=True)

                # Vendors with violations
                violating_vendors = outliers["Supplier"].dropna().unique()
                st.markdown("#### 🚩 Vendors with Violations:")
                for vendor in violating_vendors:
                    st.markdown(f"- {vendor}")

                # CSV download
                csv = outliers.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Download Flagged Data",
                    data=csv,
                    file_name=f"flagged_{sheet}.csv",
                    mime="text/csv"
                )

                # Violation frequency chart
                violation_counts = outliers["Out of Spec"].str.split(", ").explode().value_counts().reset_index()
                violation_counts.columns = ["Parameter", "Violations"]

                st.markdown("#### 📉 Frequently Violated Parameters")
                chart = alt.Chart(violation_counts).mark_bar().encode(
                    x=alt.X("Parameter", sort="-y"),
                    y="Violations",
                    tooltip=["Parameter", "Violations"]
                ).properties(width=700, height=300)
                st.altair_chart(chart, use_container_width=True)

            else:
                st.success("✅ All samples meet standard parameters.")

        except Exception as e:
            st.error(f"❌ Error processing sheet '{sheet}': {e}")

    st.markdown("---")
    st.caption("Lab Quality Flagging Dashboard | Developed by QA Team")
