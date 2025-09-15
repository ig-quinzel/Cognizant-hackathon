"""import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "trained_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")
ENCODERS_PATH = os.path.join(BASE_DIR, "encoders.pkl")

def load_model():
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    encoders = joblib.load(ENCODERS_PATH)
    return model, scaler, encoders

def predict_price(user_input, feature_cols, numeric_cols):
    model, scaler, encoders = load_model()

    # Convert categorical using encoders
    for col, encoder in encoders.items():
        val = str(user_input[col])
        if val in encoder.classes_:
            user_input[col] = encoder.transform([val])[0]
        else:
            encoder.classes_ = np.append(encoder.classes_, val)
            user_input[col] = encoder.transform([val])[0]

    # Process date
    dt = datetime.strptime(user_input['date'], '%d-%m-%Y')
    user_input['year'] = dt.year
    user_input['month'] = dt.month
    user_input['day'] = dt.day
    del user_input['date']

    # Convert to DataFrame
    input_df = pd.DataFrame([user_input])

    # Scale numeric cols
    input_df[numeric_cols] = scaler.transform(input_df[numeric_cols])

    # Reorder columns
    input_df = input_df[feature_cols]

    predicted_price = model.predict(input_df)[0]
    return round(predicted_price, 2)
"""

import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "trained_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")
ENCODERS_PATH = os.path.join(BASE_DIR, "encoders.pkl")

# Load trained components once
xgb_model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
encoders = joblib.load(ENCODERS_PATH)

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

numeric_cols = [
    'sales_units', 'competitor_price_index', 'economic_index',
    'weather_impact', 'discount_percentage', 'sales_revenue',
    'year', 'month', 'day'
]

def predict_price(user_input):
    # Convert input into DataFrame
    df = pd.DataFrame([user_input])

    # Encode categorical fields (dummy one-hot style)
    for col in ['region', 'store_type', 'category']:
        for value in encoders[f"{col}_{df[col][0]}"].classes_:
            pass  # we already trained encoders in model.py
    # Convert into one-hot style same as training
    df['region_Europe'] = 1 if df['region'][0] == "Europe" else 0
    df['region_North America'] = 1 if df['region'][0] == "North America" else 0
    df['store_type_Retail'] = 1 if df['store_type'][0] == "Retail" else 0
    df['store_type_Wholesale'] = 1 if df['store_type'][0] == "Wholesale" else 0
    df['category_Cabinets'] = 1 if df['category'][0] == "Cabinets" else 0
    df['category_Chairs'] = 1 if df['category'][0] == "Chairs" else 0
    df['category_Sofas'] = 1 if df['category'][0] == "Sofas" else 0
    df['category_Tables'] = 1 if df['category'][0] == "Tables" else 0

    # Date features
    #dt = datetime.strptime(df['date'][0], "%Y-%m-%d")
    """dt = df["date"]
    df['year'] = dt.year
    df['month'] = dt.month
    df['day'] = dt.day"""

    df["date"] = pd.to_datetime(df["date"], errors="coerce")  # ensure datetime
    if df["date"].isnull().any():
        raise ValueError("Invalid date format in input")

    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day

    df['holiday_season'] = df['holiday_season'].astype(int)
    df['promotion_applied'] = df['promotion_applied'].astype(int)


    # Drop unused original columns
    df = df.drop(['region', 'store_type', 'category', 'date'], axis=1)

    # Scale numeric features
    df[numeric_cols] = scaler.transform(df[numeric_cols])

    # Reorder columns
    df = df[feature_cols]

    # Predict
    prediction = xgb_model.predict(df)[0]
    return prediction
