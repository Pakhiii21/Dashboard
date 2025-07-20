import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Read Excel file
file_path = 'your_file.xlsx'
sheet_name = 'RWF RESULTS'
df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=4)

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

# Rename columns for easier handling
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

# Create a DataFrame of violators
violation_df = pd.DataFrame(violation_flags)
violation_df = violation_df[['Supplier', 'MFD'] + [col for col in violation_df.columns if col not in ['Supplier', 'MFD']]]

# Save the violations to a new Excel file
violation_df.to_excel('Violating_Suppliers.xlsx', index=False)

# Print sample violators
print("\nSample Violations:")
print(violation_df.head())

# Plotting example: Moisture by Supplier
plt.figure(figsize=(12, 6))
sns.barplot(data=df, x='Supplier', y='Moisture', palette='coolwarm')
plt.axhline(14, color='red', linestyle='--', label='Max Limit')
plt.axhline(8, color='green', linestyle='--', label='Min Limit')
plt.xticks(rotation=90)
plt.title('Moisture % by Supplier')
plt.legend()
plt.tight_layout()
plt.savefig('Moisture_By_Supplier.png')
plt.show()

