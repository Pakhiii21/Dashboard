import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")
st.title("🌾 Quality Parameter Checker")

uploaded_file = st.file_uploader("📁 Upload your Excel file", type=["xlsx"])
if uploaded_file:
    sheet_name = "RWF RESULTS"
    df = pd.read_excel(uploaded_file, sheet_name=sheet_name, skiprows=4)

    st.success("File uploaded and read successfully!")

    # Define standard value ranges
    standards = {
        'Moisture': (8, 14),
        'Alcoholic Acidity': (0.01, 0.12),
        'Dry Gluten': (10.5, 12),
        'Gluten Index(%)': (90, 100),
        'Total Ash %': (0, 0.56),
        'W.A.P': (60.5, 65),
        'Peak Time': (6, 8),
        'Stability': (12, 18),
        'MTI': (20, 40)
    }

    df.columns = df.columns.str.strip()

    # Create violation flags
    violation_flags = []

    for index, row in df.iterrows():
        violations = {}
        for col, (low, high) in standards.items():
            if col in row and pd.notna(row[col]):
                if not (low <= row[col] <= high):
                    violations[col] = row[col]
        if violations:
            violations['Supplier'] = row['Supplier']
            violations['MFD'] = row['MFD']
            violation_flags.append(violations)

    if violation_flags:
        violation_df = pd.DataFrame(violation_flags)
        violation_df = violation_df[['Supplier', 'MFD'] + [col for col in violation_df.columns if col not in ['Supplier', 'MFD']]]

        st.subheader("🚨 Violating Suppliers")
        st.dataframe(violation_df)

        # Download button
        st.download_button("📥 Download Violations as Excel", data=violation_df.to_csv(index=False), file_name="Violating_Suppliers.csv", mime="text/csv")

        # Moisture plot
        st.subheader("📊 Moisture % by Supplier")
        plt.figure(figsize=(12, 6))
        sns.barplot(data=df, x='Supplier', y='Moisture', palette='coolwarm')
        plt.axhline(14, color='red', linestyle='--', label='Max Limit')
        plt.axhline(8, color='green', linestyle='--', label='Min Limit')
        plt.xticks(rotation=90)
        plt.title('Moisture % by Supplier')
        plt.legend()
        st.pyplot(plt)
    else:
        st.info("✅ All values are within standard ranges.")
else:
    st.warning("Please upload an Excel file first.")
