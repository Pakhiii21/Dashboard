import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")
st.title("📊 Weekly Lab Quality Dashboard")

# File uploader
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    excel_data = pd.ExcelFile(uploaded_file)
    sheet_names = excel_data.sheet_names

    for sheet in sheet_names:
        if sheet.startswith("~"):
            continue

        st.subheader(f"📄 Sheet: `{sheet}`")
        df = pd.read_excel(uploaded_file, sheet_name=sheet)
        df = df.applymap(lambda x: "" if str(x).lower() == "none" else x)

        # Extract JFS specs from V Gluten Trend sheet
        if sheet.lower() == "v gluten trend":
            specs_row = df.iloc[0]
            specs_dict = specs_row.dropna().to_dict()
            continue

        if sheet.lower() != "rwf trend":
            continue

        # Filter out spec columns
        spec_cols = [col for col in df.columns if col in specs_dict]

        def check_violation(row):
            for col in spec_cols:
                try:
                    value = float(row[col])
                    target = float(specs_dict[col])
                    if abs(value - target) > 1e-2:  # Example tolerance
                        return "Violated"
                except:
                    continue
            return "OK"

        df["Out of Spec"] = df.apply(check_violation, axis=1)

        # Check for violations
        flagged_df = df[df["Out of Spec"] == "Violated"]

        # Show status message
        if flagged_df.empty:
            st.success("✅ All samples meet spec for this sheet.")
        else:
            st.warning("⚠️ Some samples are out of spec:")
            st.dataframe(flagged_df, use_container_width=True)

        # Unified search
        st.text_input("🔍 Search in `RWF TREND`", key=f"search_{sheet}")
        st.dataframe(df, use_container_width=True)

        # Donut chart for violations
        if not flagged_df.empty:
            for param in spec_cols:
                df_param = df[[param, "Out of Spec"]].copy()
                df_param["Status"] = df_param["Out of Spec"].apply(lambda x: "Violated" if x == "Violated" else "OK")
                chart_data = df_param["Status"].value_counts().reset_index()
                chart_data.columns = ["Status", "Count"]

                donut_chart = alt.Chart(chart_data).mark_arc(innerRadius=50).encode(
                    theta=alt.Theta(field="Count", type="quantitative"),
                    color=alt.Color(field="Status", type="nominal"),
                    tooltip=["Status", "Count"]
                ).properties(
                    title=f"{param}"
                )

                st.altair_chart(donut_chart, use_container_width=True)
