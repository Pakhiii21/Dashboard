import streamlit as st
import pandas as pd
from io import BytesIO
# Set wide layout
st.set_page_config(layout="wide")

# Page Title
st.markdown("<h2 style='color:#2c3e50;'>📊 WEEKLY DASHBOARD</h2>", unsafe_allow_html=True)

# Upload section
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

# Upload Excel file
uploaded_file = st.file_uploader("", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheet_name = st.selectbox("📄 Select a sheet to view:", xls.sheet_names)

    # Try to read skipping first row (adjust if needed)
    try:
        df = pd.read_excel(xls, sheet_name=sheet_name, skiprows=1)
    except:
        df = pd.read_excel(xls, sheet_name=sheet_name)

    # Replace NaN/None with blanks
    df.fillna("", inplace=True)

    # File and sheet info
    st.markdown(f"🗂️ **File:** `{uploaded_file.name}`  |  📄 **Sheet:** `{sheet_name}`")
    st.markdown(f" Rows: **{df.shape[0]}** | Columns: **{df.shape[1]}**")

    # Search box
    search = st.text_input("🔍 Search within data:")
    if search:
        df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]

    # Preview
    st.markdown(f"### 🔍 Preview of: `{sheet_name}`")
    st.dataframe(df, use_container_width=True, height=600)

    # Download filtered data
    @st.cache_data
    from io import BytesIO

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


    # Custom styling
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
