import streamlit as st
import pandas as pd

# Set wide layout
st.set_page_config(layout="wide")

st.markdown("<h2 style='color:#2c3e50;'>📊 Excel Dashboard Viewer</h2>", unsafe_allow_html=True)

# Upload prompt
st.markdown("""
<div style="background-color:#f9f9f9;padding:15px;border-radius:10px">
<h4>📤 Upload your Excel file</h4>
<p>Supported format: <strong>.xlsx</strong> | Max size: 200MB</p>
</div>
""", unsafe_allow_html=True)

# Upload Excel file
uploaded_file = st.file_uploader("", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheet_name = st.selectbox("📄 Select a sheet to view:", xls.sheet_names)
    df = pd.read_excel(xls, sheet_name=sheet_name)

    # Replace NaN with blank
    df.fillna("", inplace=True)

    st.markdown(f"### 🔍 Preview of: `{sheet_name}`")

    # Styled dataframe display
    st.dataframe(
        df.style.set_properties(**{
            'background-color': '#ffffff',
            'border-color': '#cccccc',
            'border-style': 'solid',
            'border-width': '1px',
            'color': '#000000'
        }),
        use_container_width=True,
        height=600
    )
