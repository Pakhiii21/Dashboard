import streamlit as st
import pandas as pd
import altair as alt

# Set wide layout
st.set_page_config(page_title="Weekly Analysis", layout="wide")

# Title
st.markdown("<h1 style='color:#2c3e50;'>📊 Weekly Analysis</h1>", unsafe_allow_html=True)

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

            # Filter
            st.markdown(f"### 📄 Sheet: {sheet}")
            search_supplier = st.text_input(f"🔍 Search Supplier in {sheet}", "")
            filtered = df[df["Supplier"].str.contains(search_supplier, case=False, na=False)]
            outliers = filtered[filtered["Out of Spec"] != "OK"]

            if not outliers.empty:
                st.warning(f"🚨 {len(outliers)} samples have parameter violations.")
                st.dataframe(outliers, use_container_width=True)

                # Show vendor names with violations
                violating_vendors = outliers["Supplier"].unique()
                st.markdown("#### 🚩 Vendors with Violations:")
                for vendor in violating_vendors:
                    st.markdown(f"- {vendor}")

                # Download filtered data
                csv = outliers.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Filtered Data as CSV",
                    data=csv,
                    file_name=f"flagged_{sheet}.csv",
                    mime="text/csv"
                )

                # Optional: Parameter violation frequency chart
                violation_counts = outliers["Out of Spec"].str.split(", ").explode().value_counts().reset_index()
                violation_counts.columns = ["Parameter", "Violations"]
                st.markdown("#### 📉 Most Frequently Violated Parameters:")
                chart = alt.Chart(violation_counts).mark_bar().encode(
                    x=alt.X("Parameter", sort="-y"),
                    y="Violations",
                    tooltip=["Parameter", "Violations"]
                ).properties(width=700, height=300)
                st.altair_chart(chart, use_container_width=True)

            else:
                st.success("✅ All samples meet standard parameters.")
        except Exception as e:
            st.error(f"Error processing sheet '{sheet}': {e}")

    st.markdown("---")
    st.caption("Lab Quality Flagging Dashboard | Developed by QA Team")
