import streamlit as st
import pandas as pd

st.set_page_config(page_title="Upload & Display Excel File", layout="centered")

st.title("📊 Upload & Display Excel File")
st.markdown("Upload any `.xlsx` Excel file below to display it directly in the dashboard.")

uploaded_file = st.file_uploader("📁 Upload Excel File", type=["xlsx"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        st.success("✅ File uploaded successfully!")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"❌ Error reading the Excel file: {e}")
else:
    st.info("👉 Please upload an Excel file to display it here.")
