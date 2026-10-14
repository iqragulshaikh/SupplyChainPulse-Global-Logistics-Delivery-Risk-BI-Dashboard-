import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score, recall_score, precision_score, f1_score
from sklearn.preprocessing import LabelEncoder

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

def train_supply_chain_models():
    print("Loading processed supply chain dataset...")
    df = pd.read_csv(PROCESSED_DIR / "processed_supply_chain.csv")

    # Encode categorical columns for machine learning
    cat_cols = df.select_dtypes(include=['object']).columns
    for col in cat_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])

    # Features and Target
    if 'Delivery_Failure' not in df.columns:
        print("ERROR: Target column 'Delivery_Failure' not found in processed data.")
        return

    X = df.drop(columns=['Delivery_Failure'])
    y = df['Delivery_Failure']

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    mlflow.set_experiment("SupplyChainPulse_Experiments")

    models = {
        "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42),
        "XGBoost": XGBClassifier(eval_metric='logloss', random_state=42)
    }

    for name, model in models.items():
        with mlflow.start_run(run_name=name):
            print(f"\nTraining {name}...")
            model.fit(X_train, y_train)

            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)[:, 1]

            auc = roc_auc_score(y_test, y_proba)
            recall = recall_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)

            print(f" -> {name} Metrics | AUC: {auc:.4f} | Recall: {recall:.4f} | F1: {f1:.4f}")

            mlflow.log_param("model_name", name)
            mlflow.log_metric("roc_auc", auc)
            mlflow.log_metric("recall", recall)
            mlflow.log_metric("precision", precision)
            mlflow.log_metric("f1_score", f1)

            # Pass all required trusted types for both RandomForest and XGBoost
            mlflow.sklearn.log_model(
                model, 
                "model", 
                skops_trusted_types=[
                    "sklearn.tree._tree.Tree", 
                    "xgboost.core.Booster", 
                    "xgboost.sklearn.XGBClassifier"
                ]
            )

    print("\nSUCCESS: All supply chain models trained and logged to MLflow successfully!")

if __name__ == "__main__":
    train_supply_chain_models()
    