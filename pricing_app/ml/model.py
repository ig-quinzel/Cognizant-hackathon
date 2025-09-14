import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
from datetime import datetime
import os

# Path for dataset
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "dataset.csv")

# Path to save model & scaler
MODEL_PATH = os.path.join(BASE_DIR, "trained_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")
ENCODERS_PATH = os.path.join(BASE_DIR, "encoders.pkl")

def train_model():
    # 1. Load dataset
    df = pd.read_csv(DATA_PATH)

    # 2. Encode categorical columns
    categorical_cols = [
        "region_Europe", "region_North America",
        "store_type_Retail", "store_type_Wholesale",
        "category_Cabinets", "category_Chairs",
        "category_Sofas", "category_Tables"
    ]

    encoders = {}
    for col in categorical_cols:
        df[col] = df[col].astype(str)
        encoders[col] = LabelEncoder()
        df[col] = encoders[col].fit_transform(df[col])

    # 3. Feature engineering (date)
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df = df.drop('date', axis=1)

    # 4. Features & target
    target_column = 'price'
    feature_cols = [
        'product_id', 'sales_units', 'holiday_season', 'promotion_applied',
        'competitor_price_index', 'economic_index', 'weather_impact',
        'discount_percentage', 'sales_revenue',
        'region_Europe', 'region_North America',
        'store_type_Retail', 'store_type_Wholesale',
        'category_Cabinets', 'category_Chairs',
        'category_Sofas', 'category_Tables',
        'year', 'month', 'day'
    ]

    X = df[feature_cols]
    y = df[target_column]

    numeric_cols = [
        'sales_units', 'competitor_price_index', 'economic_index',
        'weather_impact', 'discount_percentage', 'sales_revenue',
        'year', 'month', 'day'
    ]

    scaler = StandardScaler()
    X[numeric_cols] = scaler.fit_transform(X[numeric_cols])

    # 5. Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 6. Train model
    xgb_model = xgb.XGBRegressor(
        objective='reg:squarederror',
        n_estimators=500,
        learning_rate=0.05,
        max_depth=6,
        n_jobs=-1,
        random_state=42
    )
    xgb_model.fit(X_train, y_train)

    # 7. Evaluate
    y_pred = xgb_model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    print("✅ XGBoost Model Performance")
    print(f"MAE : {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R²  : {r2:.4f}")

    # 8. Save model, scaler, encoders
    joblib.dump(xgb_model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    joblib.dump(encoders, ENCODERS_PATH)

    return xgb_model, scaler, encoders, feature_cols, numeric_cols

if __name__ == "__main__":
    train_model()
