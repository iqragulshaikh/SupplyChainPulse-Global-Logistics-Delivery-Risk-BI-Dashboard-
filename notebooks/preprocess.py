import pandas as pd
import numpy as np
from pathlib import Path

# Paths (parent.parent points to root SupplyChainPulse/ directory)
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def preprocess_supply_chain_data():
    print("Searching for raw dataset...")
    # Find the CSV file inside data/raw/
    raw_files = list(RAW_DIR.glob("*.csv"))
    
    if not raw_files:
        print("ERROR: No CSV file found in data/raw/. Please place your dataset there.")
        return
    
    raw_path = raw_files[0]
    print(f"Loading dataset from {raw_path.name}...")
    
    # Read CSV (handling potential encoding errors common in large supply chain datasets)
    try:
        df = pd.read_csv(raw_path, encoding='latin-1')
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    print(f"Raw dataset shape: {df.shape}")

    # Data Cleaning & Feature Engineering
  
    # We will standardize key metrics for delivery risk analysis
    
    # 1. Target Variable: Check if 'Late_delivery_risk' exists, otherwise create a delay flag
    if 'Late_delivery_risk' in df.columns:
        df['Delivery_Failure'] = df['Late_delivery_risk']
    elif 'Days for shipping (real)' in df.columns and 'Days for scheduled shipping (real)' in df.columns:
        df['Delivery_Failure'] = (df['Days for shipping (real)'] > df['Days for scheduled shipping (real)']).astype(int)
    else:
        # Fallback dummy target if columns vary slightly
        df['Delivery_Failure'] = 0 

    # 2. Select and clean essential columns for logistics & financial analysis
    columns_to_keep = [
        'Type', 'Days for shipping (real)', 'Days for scheduled shipping',
        'Benefit per order', 'Sales per customer', 'Delivery Status', 
        'Late_delivery_risk', 'Category Name', 'Customer City', 
        'Customer Country', 'Market', 'Order Region', 'Shipping Mode',
        'Delivery_Failure'
    ]
    
    # Keep only columns that actually exist in the user's specific CSV variant
    available_cols = [col for col in columns_to_keep if col in df.columns]
    clean_df = df[available_cols].copy()

    # 3. Handle missing values
    clean_df = clean_df.dropna()

    # Save processed dataframe for Power BI / Tableau and ML modeling
    output_path = PROCESSED_DIR / "processed_supply_chain.csv"
    clean_df.to_csv(output_path, index=False)
    
    print(f"SUCCESS: Processed data saved successfully to {output_path}")
    print(f"Processed dataset shape: {clean_df.shape}")

if __name__ == "__main__":
    preprocess_supply_chain_data()