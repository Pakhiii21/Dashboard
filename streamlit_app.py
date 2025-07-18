import streamlit as st
import pandas as pd

st.set_page_config(page_title="Upload & Display Excel File", layout="centered")

st.title("📊 Upload & Display Excel File")
st.markdown("Upload any `.xlsx` Excel file below to explore all available sheets.")

uploaded_file = st.file_uploader("📁 Upload Excel File", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Load all sheets as a dictionary
        sheets = pd.read_excel(uploaded_file, sheet_name=None, engine='openpyxl')
        sheet_names = list(sheets.keys())

        selected_sheet = st.selectbox("Select a sheet to view:", sheet_names)

        df = sheets[selected_sheet]
        st.success(f"✅ Displaying sheet: {selected_sheet}")
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error reading the Excel file: {e}")
else:
    st.info("👉 Please upload an Excel file to view its sheets.")
