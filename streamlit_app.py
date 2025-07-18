import streamlit as st
import pandas as pd

# Set page to wide layout
st.set_page_config(layout="wide")

# Page title
st.markdown("<h2 style='color:#2c3e50;'>📊 WEEKLY DASHBOARD</h2>", unsafe_allow_html=True)

# Upload section box
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

# Upload file
uploaded_file = st.file_uploader("", type=["xlsx"])

if uploaded_file:
    # Load Excel file and select sheet
    xls = pd.ExcelFile(uploaded_file)
    sheet_name = st.selectbox("📄 Select a sheet to view:", xls.sheet_names)

    # ✅ Skip rows above actual header row if needed (e.g. skip title rows)
    df = pd.read_excel(xls, sheet_name=sheet_name, skiprows=2)  # 👈 Change 2 if needed

    # Replace NaN/None with blank
    df.fillna("", inplace=True)

    st.markdown(f"### 🔍 Preview of: `{sheet_name}`")

    # Show DataFrame with scroll and borders
    st.dataframe(
        df,
        use_container_width=True,
        height=600
    )

    # Custom border and header styling
    st.markdown("""
    <style>
    .stDataFrame tbody td {
        border: 1px solid #d3d3d3;
    }
    .stDataFrame thead th {
        background-color: #f0f0f0;
        border: 1px solid #d3d3d3;
    }
    </style>
    """, unsafe_allow_html=True)

# Hide white block and footer
st.markdown("""
<style>
.block-container {
    padding-bottom: 0rem !important;
}
footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)
