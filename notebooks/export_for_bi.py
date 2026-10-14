import pandas as pd
import numpy as np
from pathlib import Path
import joblib
from sklearn.preprocessing import LabelEncoder

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
DASHBOARDS_DIR = BASE_DIR / "dashboards"
DASHBOARDS_DIR.mkdir(parents=True, exist_ok=True)

def export_bi_dataset():
    print("Loading processed dataset for BI export...")
    df = pd.read_csv(PROCESSED_DIR / "processed_supply_chain.csv")

    # For BI reporting, we want to keep readable categorical names where possible 
    # and add model risk scores or delay flags so stakeholders can analyze them instantly.
    
    # If the model or processed data contains our target, let's create a clear financial impact column
    if 'Sales per customer' in df.columns:
        # Simulate financial exposure for delayed shipments (e.g., potential penalty or refund cost)
        df['Financial_Risk_Exposure'] = df['Sales per customer'] * 0.15
    else:
        df['Financial_Risk_Exposure'] = 100.0  # Default estimate

    # Add a clean Risk Category column for easy slicing in Power BI/Tableau
    if 'Delivery_Failure' in df.columns:
        df['Risk_Category'] = np.where(df['Delivery_Failure'] == 1, 'High Risk (Delayed)', 'Low Risk (On-Time)')
    else:
        df['Risk_Category'] = 'Standard'

    # Save final polished dataset into dashboards/ folder for Power BI / Tableau ingestion
    output_path = DASHBOARDS_DIR / "supply_chain_bi_ready.csv"
    df.to_csv(output_path, index=False)
    
    print(f"SUCCESS: BI-ready dataset exported successfully to {output_path}")
    print(f"Total rows exported: {len(df):,}")

if __name__ == "__main__":
    export_bi_dataset()