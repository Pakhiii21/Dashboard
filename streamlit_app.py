import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 Weekly Lab Quality Dashboard")

# File uploader
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    excel_data = pd.ExcelFile(uploaded_file)
    sheet_names = excel_data.sheet_names

    specs_dict = {}
    rwf_displayed = False

    for sheet in sheet_names:
        if sheet.startswith("~"):
            continue

        df = pd.read_excel(uploaded_file, sheet_name=sheet)
        df = df.applymap(lambda x: "" if str(x).lower() == "none" else x)

        if sheet.lower() == "v gluten trend":
            specs_row = df.iloc[0]
            specs_dict = specs_row.dropna().to_dict()
            continue

        if sheet.lower() != "rwf trend":
            continue

        if not rwf_displayed:
            st.subheader(f"📄 Sheet: `{sheet}`")
            spec_cols = [col for col in df.columns if col in specs_dict]

            def check_violation(row):
                for col in spec_cols:
                    try:
                        value = float(row[col])
                        target = float(specs_dict[col])
                        if abs(value - target) > 1e-2:
                            return "Violated"
                    except:
                        continue
                return "OK"

            df["Out of Spec"] = df.apply(check_violation, axis=1)

            flagged_df = df[df["Out of Spec"] == "Violated"]

            if flagged_df.empty:
                st.success("✅ All samples meet spec for this sheet.")
            else:
                st.warning("⚠️ Some samples are out of spec:")
                st.dataframe(flagged_df, use_container_width=True)

            search_term = st.text_input("🔍 Search anything in `RWF TREND`", key=f"search_{sheet}")

            if search_term:
                filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
                st.dataframe(filtered_df, use_container_width=True)
            else:
                st.dataframe(df, use_container_width=True)

            rwf_displayed = True
