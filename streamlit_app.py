import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Weekly Analysis", layout="wide")

st.markdown("<h1 style='color:#4B8BBE;'>📊 Weekly Analysis Dashboard</h1>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

# Define parameter thresholds
standards = {
    "DRC": {"min": 38},
    "TPS": {"min": 38, "max": 50},
    "Pizza Sauce": {"min": 38}
}

def check_violations(df, standards):
    violations = pd.DataFrame()
    for param, rules in standards.items():
        if param in df.columns:
            if "min" in rules:
                violations = pd.concat([violations, df[df[param] < rules["min"]]])
            if "max" in rules:
                violations = pd.concat([violations, df[df[param] > rules["max"]]])
    return violations.drop_duplicates()

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheets = xls.sheet_names

    for sheet in sheets:
        st.markdown(f"### 📄 Sheet: {sheet}")
        df = pd.read_excel(uploaded_file, sheet_name=sheet, skiprows=4)
        df.dropna(axis=1, how='all', inplace=True)

        if 'Supplier' not in df.columns:
            st.error("⚠️ 'Supplier' column not found in this sheet!")
            continue

        # --- Search Feature ---
        search_term = st.text_input(f"🔍 Search Supplier in {sheet}", key=sheet)
        filtered_df = df[df['Supplier'].astype(str).str.contains(search_term, case=False, na=False)] if search_term else df

        # --- Show Violations ---
        if sheet == 'RWF RESULTS':
            violated = check_violations(filtered_df, standards)
            if not violated.empty:
                st.warning("🚨 Vendors violating standard values:")
                st.dataframe(violated[['Supplier'] + list(standards.keys())].drop_duplicates())
                # Optional: Plot violation counts
                violation_counts = violated['Supplier'].value_counts().reset_index()
                violation_counts.columns = ['Supplier', 'Violations']
                fig = px.bar(violation_counts, x='Supplier', y='Violations', color='Violations',
                             title='Number of Parameter Violations per Supplier')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.success("✅ No violations found based on defined standards.")

        # --- Display Filtered Data ---
        st.dataframe(filtered_df)

        # --- Download Filtered Data ---
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(f"📥 Download filtered data from {sheet}", csv, f"{sheet}_filtered.csv", "text/csv")

