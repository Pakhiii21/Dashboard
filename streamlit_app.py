import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Set page layout
st.set_page_config(page_title="Weekly Lab Dashboard", layout="wide")

st.markdown("<h1 style='color:#2c3e50;'>📊 Weekly Lab Dashboard</h1>", unsafe_allow_html=True)

# Upload Excel file
uploaded_file = st.file_uploader("📤 Upload lab Excel file (.xlsx)", type=[".xlsx"])

# Define parameter specification limits (JFS)
limits = {
    "Moisture %": (0.08, 0.14),
    "Alcoholic Acidity %": (0.01, 0.12),
    "Dry Gluten %": (0.105, 0.12),
    "Gluten Index %": (0.90, None),
    "Total Ash %": (None, 0.0056),
    "WAP": (0.605, 0.65),
    "Peak Time": (6, 8),
    "Stability": (12, 18),
    "MTI": (20, 40),
    "TPS": (38, 100),
    "DRC": (38, None)
}

# Utility function to check if value is within spec
def check_limits(row, limits):
    issues = []
    for param, (low, high) in limits.items():
        val = row.get(param)
        if pd.isna(val):
            continue
        if (low is not None and val < low) or (high is not None and val > high):
            issues.append(param)
    return ", ".join(issues) if issues else "OK"

# Master dataframe to collect all sheets
master_df = pd.DataFrame()

if uploaded_file:
    excel = pd.ExcelFile(uploaded_file)

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

            # Convert numeric columns
            for col in limits:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # Check limits
            df["Out of Spec"] = df.apply(lambda row: check_limits(row, limits), axis=1)

            # Add sheet name
            df["Sheet"] = sheet

            # Append to master
            master_df = pd.concat([master_df, df], ignore_index=True)
        except Exception as e:
            st.error(f"❌ Error processing sheet '{sheet}': {e}")

    if not master_df.empty:
        # ✅ Safely convert MFD to datetime
        master_df["MFD"] = pd.to_datetime(master_df["MFD"], errors='coerce')

        if master_df["MFD"].isna().any():
            st.warning("⚠️ Some MFD entries could not be parsed as dates and were excluded.")

        # Filters
        with st.sidebar:
            st.markdown("## 🔎 Filters")
            suppliers = master_df["Supplier"].dropna().unique()
            selected_supplier = st.multiselect("Filter by Supplier", suppliers, default=list(suppliers))

            min_date = master_df["MFD"].min()
            max_date = master_df["MFD"].max()
            selected_date = st.slider("Filter by MFD", min_value=min_date, max_value=max_date,
                                      value=(min_date, max_date))

        filtered_df = master_df[
            (master_df["Supplier"].isin(selected_supplier)) &
            (master_df["MFD"].between(*selected_date))
        ]

        # Highlight violation status
        def highlight_violations(val):
            if val == "OK":
                return "background-color: #d4edda; color: black"
            else:
                return "background-color: #f8d7da; color: black"

        st.markdown("## ✅ Full Summary Table")
        styled = filtered_df.style.applymap(highlight_violations, subset=["Out of Spec"])
        st.dataframe(styled, use_container_width=True)

        # Download full report
        csv = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Master Report (CSV)", data=csv, file_name="lab_summary.csv", mime="text/csv")

        # Vendor vs Parameter Heatmap
        st.markdown("## 🔥 Violation Heatmap (Vendor × Parameter)")
        matrix_df = filtered_df[filtered_df["Out of Spec"] != "OK"].copy()
        exploded = matrix_df.assign(Param=matrix_df["Out of Spec"].str.split(", ")).explode("Param")
        heatmap_data = exploded.pivot_table(index="Supplier", columns="Param", aggfunc="size", fill_value=0)

        if not heatmap_data.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(heatmap_data, annot=True, fmt="d", cmap="Reds", ax=ax)
            st.pyplot(fig)
        else:
            st.info("No violations to display in heatmap.")

        # Parameter trend over time
        st.markdown("## 📈 Parameter Trends Over Time")
        param = st.selectbox("Select Parameter", list(limits.keys()))
        if param in filtered_df.columns:
            trend_chart = alt.Chart(filtered_df.dropna(subset=[param])).mark_line(point=True).encode(
                x="MFD:T",
                y=alt.Y(param, title=f"{param}"),
                color="Supplier",
                tooltip=["Supplier", "MFD", param]
            ).properties(width=800, height=350)
            st.altair_chart(trend_chart, use_container_width=True)

        # Per-supplier parameter bar chart
        st.markdown("## 📊 Parameter Values per Supplier")
        melted = filtered_df.melt(id_vars=["Supplier", "MFD"], value_vars=list(limits.keys()),
                                  var_name="Parameter", value_name="Value")
        bar_chart = alt.Chart(melted.dropna()).mark_bar().encode(
            x=alt.X("Supplier:N", sort="-y"),
            y="Value:Q",
            color="Parameter:N",
            column="Parameter:N",
            tooltip=["Supplier", "Parameter", "Value"]
        ).resolve_scale(y='independent').properties(height=250)
        st.altair_chart(bar_chart, use_container_width=True)

        st.caption("Lab Quality Analysis Dashboard | Enhanced by QA Automation 🧪")
