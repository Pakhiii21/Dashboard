import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.title("Jubilant Lab Weekly Dashboard")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file is not None:
    xls = pd.ExcelFile(uploaded_file)
    
    # Start your logic here
    results_raw = pd.read_excel(xls, sheet_name="RWF RESULTS", header=None, skiprows=5)
    trend_raw = pd.read_excel(xls, sheet_name="RWF TREND", header=None, skiprows=1)
    
    # Continue with your data processing...


# Step 1: Read sheets with raw headers
results_raw = pd.read_excel(xls, sheet_name="RWF RESULTS", header=None, skiprows=5)
trend_raw = pd.read_excel(xls, sheet_name="RWF TREND", header=None, skiprows=2)

# Step 2: Use first data row as header
results_raw.columns = results_raw.iloc[0]
results_df = results_raw.drop(index=0).reset_index(drop=True)

trend_raw.columns = trend_raw.iloc[0]
trend_df = trend_raw.drop(index=0).reset_index(drop=True)

# Step 3: Clean up and rename columns
results_df.columns = [str(col).strip() for col in results_df.columns]
trend_df.columns = [str(col).strip() for col in trend_df.columns]

# Step 4: Rename first column to 'Vendor'
if "Vendor" not in trend_df.columns:
    trend_df.rename(columns={trend_df.columns[0]: "Vendor"}, inplace=True)

if "Vendor" not in results_df.columns:
    results_df.rename(columns={results_df.columns[0]: "Vendor"}, inplace=True)

# Step 5: Define parameters to compare
parameters = ['Moisture %', 'Protein %', 'Total Ash %', 'Peak Time', 'Stability']
mapped_trend_cols = {}
for col in trend_df.columns:
    for param in parameters:
        if param.lower() in col.lower():
            mapped_trend_cols[param] = col

# Step 6: Merge average values with each vendor observation
results_df['Vendor'] = results_df['Vendor'].astype(str).str.strip()
trend_df['Vendor'] = trend_df['Vendor'].astype(str).str.strip()

# Convert numeric cols
for param in parameters:
    if param in results_df.columns:
        results_df[param] = pd.to_numeric(results_df[param], errors='coerce')

    if param in mapped_trend_cols:
        trend_df[mapped_trend_cols[param]] = pd.to_numeric(trend_df[mapped_trend_cols[param]], errors='coerce')

# Merge average (target) values
merged_df = pd.merge(results_df, trend_df[['Vendor'] + list(mapped_trend_cols.values())], on='Vendor', how='left')

# Step 7: Check compliance and report
non_compliant = []

for param in parameters:
    observed_col = param
    expected_col = mapped_trend_cols.get(param)
    if observed_col in merged_df.columns and expected_col:
        merged_df[f"{param} OK"] = abs(merged_df[observed_col] - merged_df[expected_col]) <= 1.0  # tolerance
        non_ok = merged_df[~merged_df[f"{param} OK"]]

        if not non_ok.empty:
            non_compliant.append((param, non_ok['Vendor'].unique().tolist()))

# Show non-compliance report
print("🚨 Non-Compliant Vendors:")
for param, vendors in non_compliant:
    print(f"- {param}: {', '.join(vendors)}")

# Step 8: Plot observed vs expected
import plotly.graph_objects as go

for param in parameters:
    observed_col = param
    expected_col = mapped_trend_cols.get(param)
    if observed_col in merged_df.columns and expected_col:
        fig = px.scatter(
            merged_df,
            x='Vendor',
            y=[observed_col, expected_col],
            title=f"{param} - Observed vs Expected",
            labels={"value": param, "variable": "Type"},
        )
        fig.update_layout(xaxis_tickangle=-45)
        fig.show()
