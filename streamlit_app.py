import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(layout="wide")

st.markdown("<h1 style='text-align: center; color: #2c3e50;'>📊 Weekly Analysis Dashboard</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📂 Upload Excel File", type=["xlsx"])

if uploaded_file:
    # Define parameter thresholds (add more as needed)
    thresholds = {
        'Moisture': (11.5, 13.5),
        'Protein': (9.0, 11.5),
        'Water Absorption': (58, 63),
        'Gluten': (8.0, 12.5),
        'Starch Damage': (5, 9),
        'TPS': (38, 38),
        'Pizza Sauce': (38, 100),
        'MDRC': (38, 100),
    }

    excel_data = pd.ExcelFile(uploaded_file)
    violation_summary = []
    violation_counts = {}

    for sheet in excel_data.sheet_names:
        st.markdown(f"### 📄 Sheet: `{sheet}`")
        df = excel_data.parse(sheet)

        if 'Mill Name' not in df.columns:
            st.warning(f"`Mill Name` column not found in `{sheet}`. Skipping.")
            continue

        # Rename to standard name
        df['Supplier'] = df['Mill Name']

        # Search bar
        search_term = st.text_input(f"🔍 Search vendor in `{sheet}`", key=f"search_{sheet}")
        if search_term:
            df = df[df['Supplier'].astype(str).str.contains(search_term, case=False, na=False)]

        # Flag violations
        violations = pd.DataFrame(columns=df.columns)
        for param, (min_val, max_val) in thresholds.items():
            if param in df.columns:
                out_of_range = df[(df[param] < min_val) | (df[param] > max_val)]
                violations = pd.concat([violations, out_of_range])

                # Count for graph
                count = out_of_range.shape[0]
                if count > 0:
                    violation_counts[param] = violation_counts.get(param, 0) + count

        violations.drop_duplicates(inplace=True)

        if not violations.empty:
            st.error("⚠️ Some vendors are not meeting standards:")
            st.dataframe(violations, use_container_width=True)

            vendors = violations['Supplier'].unique().tolist()
            st.markdown("**🧾 Vendors with Violations:** " + ", ".join(vendors))

            # Download filtered data
            csv = violations.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download Violations", csv, f"{sheet}_violations.csv", "text/csv")
        else:
            st.success("✅ All values within standard range.")

    # Show bar chart
    if violation_counts:
        st.markdown("### 📊 Violation Frequency by Parameter")
        fig, ax = plt.subplots()
        ax.bar(violation_counts.keys(), violation_counts.values(), color='tomato')
        ax.set_ylabel("Violation Count")
        ax.set_title("Most Frequently Violated Parameters")
        plt.xticks(rotation=45)
        st.pyplot(fig)
