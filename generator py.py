import pandas as pd
import numpy as np
import random

# 1. Setup Parameters
n_rows = 1000
drugs = [
    ('Insulin', 'Biologic', 'Cold Chain'), ('Amoxicillin', 'Antibiotic', 'Ambient'),
    ('Pembrolizumab', 'Oncology', 'Cold Chain'), ('Atorvastatin', 'Statin', 'Ambient'),
    ('Salbutamol', 'Inhaler', 'Ambient'), ('Adrenaline', 'Emergency', 'Cold Chain')
]

# 2. Generate Base Data
data = {
    'SKU_ID': [f'PH-UK-{1000+i}' for i in range(n_rows)],
    'Drug_Name': [random.choice(drugs)[0] for _ in range(n_rows)],
    'Category': [next(d[1] for d in drugs if d[0] == name) for name in [random.choice(drugs)[0] for _ in range(n_rows)]],
    'Storage_Req': [next(d[2] for d in drugs if d[0] == name) for name in [random.choice(drugs)[0] for _ in range(n_rows)]],
    'Current_Stock': np.random.randint(500, 5000, n_rows),
    'Monthly_Demand': np.random.randint(800, 4500, n_rows),
    'Unit_Cost_GBP': np.round(np.random.uniform(5.0, 500.0, n_rows), 2),
    'Lead_Time_Base_Days': np.random.randint(5, 15, n_rows),
    'Route': np.random.choice(['Dover-Calais', 'Felixstowe', 'Heathrow Air', 'Eurotunnel'], n_rows, p=[0.4, 0.2, 0.1, 0.3])
}

df = pd.DataFrame(data)

# 3. Add the "Brexit & Risk" Logic
# Dover and Eurotunnel are highly susceptible to "Customs Friction"
df['Customs_Delay_Factor'] = df['Route'].apply(lambda x: np.random.uniform(1.5, 3.0) if x in ['Dover-Calais', 'Eurotunnel'] else 1.1)
df['Predicted_Lead_Time'] = (df['Lead_Time_Base_Days'] * df['Customs_Delay_Factor']).round(1)

# Calculate Risk Score (0-100)
# High risk = Low stock + High Lead Time + Cold Chain (urgency)
df['Stock_Runway_Days'] = (df['Current_Stock'] / (df['Monthly_Demand'] / 30)).round(1)
df['Risk_Score'] = (100 - (df['Stock_Runway_Days'] * 2) + (df['Predicted_Lead_Time'] * 3)).clip(0, 100)

# 4. Save to CSV
df.to_csv('UK_Pharma_Supply_Risk.csv', index=False)
print("Dataset 'UK_Pharma_Supply_Risk.csv' generated successfully!")