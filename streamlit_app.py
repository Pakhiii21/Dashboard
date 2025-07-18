import streamlit as st
import pandas as pd
import io
import plotly.express as px

# Set wide layout
st.set_page_config(layout="wide")

# Page Title
st.markdown("<h2 style='color:#0b5394;'>📊 WEEKLY DASHBOARD</h2>", unsafe_allow_html=True)

# Upload section
st.markdown("""
<div style="
    background-color:#e6f0f5;
    padding:16px;
    border-radius:10px;
    border:1px solid #d0dce0;
    color:#1c1c1c;
">
    <h4 style="margin-bottom:8px;">Upload your Excel file</h4>
    <p style="margin:0;">Supported format: <strong>.xlsx</strong> | Max size: 200MB</p>
</div>
""", unsafe_allow_html=True)

# Upload Excel file
uploaded_file = st.file_uploader("", type=["xlsx"])

if uploaded_file:
    try:
        xls = pd.ExcelFile(uploaded_file)
        sheet_name = st.selectbox("Select a sheet to view:", xls.sheet_names)

        try:
            df = pd.read_excel(xls, sheet_name=sheet_name, skiprows=4 if sheet_name == "RWF RESULTS" else 0)
        except Exception as e:
            st.error(f"Error reading sheet: {e}")
            st.stop()

        df.fillna("", inplace=True)

        st.markdown(f"**File:** `{uploaded_file.name}`  |  **Sheet:** `{sheet_name}`")
        st.markdown(f"Rows: **{df.shape[0]}** | Columns: **{df.shape[1]}**")

        # Auto-detect relevant columns
        col_map = {}
        for col in df.columns:
            col_str = str(col).lower()
            if "supplier" in col_str or "vendor" in col_str:
                col_map['vendor'] = col
            if "moisture" in col_str:
                col_map['moisture'] = col
            if "protein" in col_str:
                col_map['protein'] = col
            if "ash" in col_str:
                col_map['ash'] = col
            if "drc" in col_str:
                col_map['drc'] = col
            if "tps" in col_str:
                col_map['tps'] = col

        # Show all available columns (for debugging)
        st.write("Detected columns:", col_map)

        for key in ['moisture', 'protein', 'ash', 'drc', 'tps']:
            if key in col_map:
                df[col_map[key]] = pd.to_numeric(df[col_map[key]], errors="coerce")

        # Apply compliance rules
        if 'moisture' in col_map:
            df["Moisture OK"] = df[col_map['moisture']].between(3, 10)
        if 'protein' in col_map:
            df["Protein OK"] = df[col_map['protein']].between(80, 93)
        if 'ash' in col_map:
            df["Ash OK"] = df[col_map['ash']].between(0.8, 2)
        if 'drc' in col_map:
            df["DRC OK"] = df[col_map['drc']] >= 38
        if 'tps' in col_map:
            df["TPS OK"] = df[col_map['tps']] >= 38

        check_cols = [col for col in ["Moisture OK", "Protein OK", "Ash OK", "DRC OK", "TPS OK"] if col in df.columns]
        if check_cols:
            df["All OK"] = df[check_cols].all(axis=1)

        # Highlight non-compliant vendors
        if 'vendor' in col_map:
            st.markdown("### Vendors Not Meeting All Criteria")
            non_compliant = df[df.get("All OK") == False]
            if not non_compliant.empty:
                st.dataframe(non_compliant[[col_map['vendor']] + check_cols], use_container_width=True)
                bad_vendors = non_compliant[col_map['vendor']].unique().tolist()
                st.warning(f"The following vendors have one or more non-compliant records: {', '.join(map(str, bad_vendors))}")
            else:
                st.success("All vendors meet the defined quality parameters.")

        # Plot graphs
        st.markdown("### Parameter Distributions")
        for key in ['moisture', 'protein', 'ash']:
            if key in col_map:
                fig = px.box(df, y=col_map[key], points="all", title=f"{key.title()} % Distribution")
                st.plotly_chart(fig, use_container_width=True)

        # Search
        search = st.text_input("Search within data:")
        if search:
            df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]

        st.markdown(f"### Preview of: `{sheet_name}`")
        st.dataframe(df, use_container_width=True, height=600)

        @st.cache_data
        def convert_df(df):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            return output.getvalue()

        excel_bytes = convert_df(df)
        st.download_button(
            label="Download Filtered Data as Excel",
            data=excel_bytes,
            file_name="filtered_dashboard.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Unable to read file: {e}")

# Styling
st.markdown("""
<style>
.stDataFrame tbody td {
    white-space: normal;
    word-wrap: break-word;
    border: 1px solid #d3d3d3;
}
.stDataFrame thead th {
    background-color: #f0f0f0;
    border: 1px solid #d3d3d3;
}
.block-container {
    padding-bottom: 0rem !important;
}
footer {
    visibility: hidden;
}
body, .stApp {
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 15px;
}
</style>
""", unsafe_allow_html=True)
