import streamlit as st
import pandas as pd
from io import BytesIO  # Make sure this is at the top

# Set page layout to wide
st.set_page_config(layout="wide")

# Title
st.markdown("<h2 style='color:#2c3e50;'>📊 WEEKLY DASHBOARD</h2>", unsafe_allow_html=True)

# Upload section (styled)
st.markdown("""
<div style="
    background-color:#e6f0f5;
    padding:16px;
    border-radius:10px;
    border:1px solid #d0dce0;
    color:#1c1c1c;
">
    <h4 style="margin-bottom:8px;">📤 Upload your Excel file</h4>
    <p style="margin:0;">Supported format: <strong>.xlsx</strong> | Max size: 200MB</p>
</div>
""", unsafe_allow_html=True)

# Upload the file
uploaded_file = st.file_uploader("", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheet_name = st.selectbox("📄 Select a sheet to view:", xls.sheet_names)

    # Let user choose rows to skip (default 0, but often 1 if heading is not in row 1)
    skip_rows = st.number_input("🔢 Rows to skip (if actual headers start later)", min_value=0, max_value=10, value=0, step=1)

    # Load data from the selected sheet
    df = pd.read_excel(xls, sheet_name=sheet_name, skiprows=skip_rows)
    df.fillna("", inplace=True)  # Replace NaN with blanks

    st.markdown(f"### 🔍 Preview of: `{sheet_name}`")

    # Show table with scroll + borders
    st.dataframe(df, use_container_width=True, height=600)

    # Styling for table borders and background
    st.markdown("""
    <style>
    .stDataFrame tbody td {
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
    </style>
    """, unsafe_allow_html=True)

    # Convert dataframe to Excel bytes for download
    @st.cache_data
    def convert_df(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        return output.getvalue()

    excel_bytes = convert_df(df)

    st.download_button(
        label="📥 Download Filtered Data as Excel",
        data=excel_bytes,
        file_name="filtered_dashboard.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
