import streamlit as st
import pandas as pd

# Set full-width layout
st.set_page_config(layout="wide")

# Header
st.markdown("<h2 style='color:#2c3e50;'>📊 WEEKLY DASHBOARD</h2>", unsafe_allow_html=True)

# Upload box with soft background
st.markdown("""
<div style="background-color:#f9f9f9;padding:15px;border-radius:10px">
<h4>📤 Upload your Excel file</h4>
<p>Supported format: <strong>.xlsx</strong> | Max size: 200MB</p>
</div>
""", unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader("", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheet_name = st.selectbox("📄 Select a sheet to view:", xls.sheet_names)
    df = pd.read_excel(xls, sheet_name=sheet_name)

    # Replace None/NaN with blank cell
    df_display = df.fillna("")

    st.markdown(f"### 🔍 Preview of: `{sheet_name}`")

    # Convert DataFrame to HTML with styling
    html_table = df_display.to_html(classes='styled-table', index=False, border=0)

    # Inject CSS styles
    st.markdown("""
    <style>
    /* Set dashboard background color */
    body {
        background-color: #f9f9f9;
    }

    .styled-table {
      border-collapse: collapse;
      width: 100%;
      font-size: 16px;
      background-color: #ffffff;
    }

    .styled-table th, .styled-table td {
      border: 1px solid #ccc;
      padding: 8px;
      text-align: left;
    }

    .styled-table th {
      background-color: #f0f0f0;
      font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    # Show the styled HTML table
    st.markdown(html_table, unsafe_allow_html=True)
