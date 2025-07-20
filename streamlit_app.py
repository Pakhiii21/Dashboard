import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")

st.title("🧪 Lab Dashboard: Vendor Compliance vs JFS Specs")

uploaded_file = st.file_uploader("📤 Upload your Excel file", type=["xlsx"])

if uploaded_file is not None:
    # Load Excel sheets
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names

    # Display sheet options
    st.sidebar.subheader("📄 Sheet Selection")
    sheet = st.sidebar.selectbox("Select sheet to analyze", sheet_names)

    # Load the selected sheet
    master_df = xls.parse(sheet)

    # Normalize column names
    master_df.columns = master_df.columns.str.strip()

    if "MFD" not in master_df.columns:
        st.error("❌ 'MFD' (Manufacture Date) column is missing in the selected sheet.")
        st.stop()

    # Convert MFD to datetime safely
    master_df["MFD"] = pd.to_datetime(master_df["MFD"], errors='coerce')

    # Warn if any dates failed to parse
    if master_df["MFD"].isna().any():
        st.warning("⚠️ Some values in 'MFD' column could not be parsed as dates and have been ignored.")

    # Drop rows with NaT in MFD
    valid_dates = master_df["MFD"].dropna()

    if valid_dates.empty:
        st.error("❌ No valid dates in 'MFD'. Please check the format.")
        st.stop()

    # Date range filter
    min_date = valid_dates.min()
    max_date = valid_dates.max()

    selected_date = st.slider("📅 Filter by MFD", min_value=min_date, max_value=max_date,
                              value=(min_date, max_date), format="YYYY-MM-DD")

    # Filter dataframe
    filtered_df = master_df[(master_df["MFD"] >= selected_date[0]) & (master_df["MFD"] <= selected_date[1])]

    # Display vendor filter
    if "Vendor" not in filtered_df.columns:
        st.error("❌ 'Vendor' column not found.")
        st.stop()

    vendors = filtered_df["Vendor"].dropna().unique()
    selected_vendors = st.sidebar.multiselect("🏷️ Filter by Vendor", vendors, default=list(vendors))

    filtered_df = filtered_df[filtered_df["Vendor"].isin(selected_vendors)]

    st.subheader("📊 Parameter Trends vs JFS Specs")

    # Identify parameter columns (excluding metadata columns)
    metadata_cols = ["MFD", "Vendor", "Batch No", "Product Name"]
    parameter_cols = [col for col in filtered_df.columns if col not in metadata_cols and filtered_df[col].dtype != "O"]

    for param in parameter_cols:
        fig, ax = plt.subplots(figsize=(10, 4))
        sns.lineplot(data=filtered_df, x="MFD", y=param, hue="Vendor", marker="o", ax=ax)

        ax.set_title(f"{param} Over Time")
        ax.set_xlabel("MFD")
        ax.set_ylabel(param)

        # Plot JFS Specs if available
        spec_row = master_df.loc[master_df["Vendor"] == "JFS Specs"]
        if not spec_row.empty and param in spec_row.columns:
            spec_value = pd.to_numeric(spec_row[param], errors='coerce').values[0]
            if not np.isnan(spec_value):
                ax.axhline(y=spec_value, color="red", linestyle="--", label="JFS Spec")
                ax.legend()

        st.pyplot(fig)

    st.subheader("🧾 Summary Table")
    st.dataframe(filtered_df)

    # Highlight out-of-spec values (optional)
    def highlight_out_of_spec(row):
        styles = []
        for col in parameter_cols:
            val = row[col]
            try:
                spec_val = float(spec_row[col].values[0])
                if pd.notna(val) and pd.notna(spec_val) and val > spec_val:
                    styles.append('background-color: #ffdddd')
                else:
                    styles.append('')
            except:
                styles.append('')
        return styles

    if not spec_row.empty:
        st.write("🔍 Highlighted rows with out-of-spec values")
        styled_df = filtered_df.style.apply(highlight_out_of_spec, axis=1)
        st.dataframe(styled_df)

else:
    st.info("📂 Please upload an Excel file to begin.")
