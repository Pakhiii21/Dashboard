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

    specs_dict = {}

    # Load V Gluten Trend first to extract specs
    if "V Gluten Trend" in [s.strip().lower() for s in sheet_names]:
        gluten_sheet = [s for s in sheet_names if s.strip().lower() == "v gluten trend"][0]
        df_specs = pd.read_excel(uploaded_file, sheet_name=gluten_sheet)
        df_specs = df_specs.applymap(lambda x: "" if str(x).lower() == "none" else x)
        specs_row = df_specs.iloc[0]
        specs_dict = specs_row.dropna().to_dict()

    for sheet in sheet_names:
        if sheet.startswith("~") or sheet.strip().lower() == "v gluten trend":
            continue

        st.subheader(f"📄 Sheet: `{sheet}`")
        df = pd.read_excel(uploaded_file, sheet_name=sheet)
        df = df.applymap(lambda x: "" if str(x).lower() == "none" else x)

        # Filter out spec columns
        spec_cols = [col for col in df.columns if col in specs_dict]

        def check_violation(row):
            for col in spec_cols:
                try:
                    value = float(row[col])
                    target = float(specs_dict[col])
                    if abs(value - target) > 1e-2:  # tolerance
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

        st.text_input(f"🔍 Search in `{sheet}`", key=f"search_{sheet}")
        st.dataframe(df, use_container_width=True)

        # Graphs for violated parameters
        violated_params = []
        for param in spec_cols:
            try:
                target = float(specs_dict[param])
                violated = df[param].apply(lambda x: abs(float(x) - target) > 1e-2 if str(x).replace('.', '', 1).isdigit() else False)
                if violated.any():
                    violated_params.append(param)
            except:
                continue

        if violated_params:
            st.subheader("📊 Actual vs Target for Violated Parameters")
            for param in violated_params:
                try:
                    df_valid = df[df[param].apply(lambda x: str(x).replace('.', '', 1).isdigit())].copy()
                    df_valid[param] = df_valid[param].astype(float)
                    df_valid["Target Spec"] = float(specs_dict[param])

                    df_melt = df_valid.melt(value_vars=[param, "Target Spec"],
                                            var_name="Type", value_name="Value")

                    chart = alt.Chart(df_melt).mark_bar().encode(
                        x=alt.X("Type:N"),
                        y=alt.Y("Value:Q", title=param),
                        color=alt.Color("Type:N"),
                        tooltip=["Type", "Value"]
                    ).properties(
                        title=f"{param} - Actual vs Target",
                        width=400
                    )

                    st.altair_chart(chart, use_container_width=True)
                except:
                    continue
        else:
            st.info("✅ No parameter violations to display in chart.")
