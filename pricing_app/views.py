from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import SuperUserLoginForm

def superuser_login(request):
    if request.method == 'POST':
        form = SuperUserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SuperUserLoginForm()
    return render(request, 'pricing_app/login.html', {'form': form})


@login_required
def dashboard(request):
    return render(request, 'pricing_app/dashboard.html')



from django.shortcuts import render
from .forms import PricePredictionForm
from .ml.predictor import predict_price
#from .ml.model import xgb_model, X_train


def quote_form(request):
    if request.method == "POST":
        form = PricePredictionForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            predicted_price = predict_price(data)

            # --- Fix: prepare session data ---
            session_data = data.copy()

            # Convert date object to string for JSON serialization
            if "date" in session_data and hasattr(session_data["date"], "isoformat"):
                session_data["date"] = session_data["date"].isoformat()

            # Ensure predicted_price is a float (not numpy type)
            request.session["prediction_result"] = {
                "data": session_data,
                "predicted_price": float(predicted_price),
            }

            # Redirect to result page
            return render(request, "pricing_app/quote_result.html", {
                "predicted_price": predicted_price,
                "input_data": data
            })
    else:
        form = PricePredictionForm()
    return render(request, "pricing_app/quote_form.html", {"form": form})




def quote_description(request):
    session_data = request.session.get("prediction_result")

    if not session_data:
        # If user directly visits without prediction, go back
        return redirect("quote_form")

    data = session_data["data"]
    predicted_price = session_data["predicted_price"]

    # Compute competitor price (example calculation)
    competitor_price = data['competitor_price_index'] * data['sales_revenue']

    # Prepare chart data
    chart_data = {
        "predicted_price": predicted_price,
        "competitor_price": competitor_price,
        "discount_percentage": data['discount_percentage'],
        "holiday_season": int(data['holiday_season']),
        "promotion_applied": int(data['promotion_applied']),
        "sales_units": data['sales_units'],
        "economic_index": data['economic_index'],
        "weather_impact": data['weather_impact'],
    }

    predicted_price = chart_data["predicted_price"]
    explanations = {}

    # Dynamic explanation logic
    sales_units = chart_data["sales_units"]
    if sales_units > 500:
        explanations["sales_units"] = f"High sales units ({sales_units}) suggest strong demand, supporting a higher predicted price."
    else:
        explanations["sales_units"] = f"Relatively low sales units ({sales_units}) indicate weaker demand, which reduces pricing power."

    economic_index = chart_data["economic_index"]
    if economic_index >= 70:
        explanations["economic_index"] = f"Economic index of {economic_index} reflects strong market conditions, allowing higher pricing."
    elif economic_index >= 40:
        explanations["economic_index"] = f"Economic index of {economic_index} indicates moderate conditions, stabilizing prices."
    else:
        explanations["economic_index"] = f"Low economic index of {economic_index} reflects weak demand, pulling predicted price down."

    weather_impact = chart_data["weather_impact"]
    if weather_impact > 50:
        explanations["weather_impact"] = f"Weather impact score {weather_impact} suggests favorable conditions, boosting sales and supporting higher prices."
    else:
        explanations["weather_impact"] = f"Weather impact score {weather_impact} shows unfavorable conditions, reducing sales and lowering prices."

    discount_percentage = chart_data["discount_percentage"]
    if discount_percentage > 0:
        discounted_price = predicted_price * (1 - discount_percentage/100)
        explanations["discount_percentage"] = f"A discount of {discount_percentage}% reduces the predicted price to about ${discounted_price:.2f}."
    else:
        explanations["discount_percentage"] = "No discount applied, so the predicted price remains at its full estimated value."


    return render(request, "pricing_app/quote_description.html", {
        "predicted_price": predicted_price,
        "input_data": data,
        "chart_data": chart_data,
        "explanations": explanations,
    })


    """SHAP PLOT (Feature importance) 
import shap
explainer = shap.Explainer(xgb_model, X_train)
shap_values = explainer(X_test)
shap.plots.force(shap_values[0])

shap.plots.beeswarm(shap_values)
user_shap_values = explainer(input_df)

shap_df = pd.DataFrame({
    'Feature': input_df.columns,
    'Value': input_df.iloc[0],
    'SHAP_Contribution': user_shap_values.values[0]
}).sort_values(by='SHAP_Contribution', key=abs, ascending=False)

print(shap_df)"""


"""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from statsmodels.tsa.statespace.sarimax import SARIMAX

df = pd.read_csv("demand_forecasting_dataset.csv")
df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
df = df.dropna(subset=['date']).sort_values("date")
df = df.replace({"TRUE": 1, "FALSE": 0, True: 1, False: 0})
label_enc = LabelEncoder()
for col in df.columns:
    if df[col].dtype == "object" and col not in ["date"]:
        df[col] = label_enc.fit_transform(df[col].astype(str))

df['sales_units'] = np.log1p(df['sales_units'])
df['sales_revenue'] = np.log1p(df['sales_revenue'])

for lag in [1, 7, 14]:
    df[f'lag_sales_{lag}'] = df['sales_units'].shift(lag)

df['rolling_mean_sales_7'] = df['sales_units'].rolling(window=7).mean()
df['rolling_std_sales_7'] = df['sales_units'].rolling(window=7).std()

df['price'] = np.log1p(df['price'])
df['price_change'] = df['price'].pct_change()
df['price_rolling_mean_7'] = df['price'].rolling(window=7).mean()

df = df.dropna()


y = df['sales_units']  
exog_features = [
    'holiday_season', 'promotion_applied',
    'competitor_price_index', 'economic_index', 'weather_impact',
    'discount_percentage', 'sales_revenue', 'price',
    'price_change', 'price_rolling_mean_7',
    'category_Cabinets', 'category_Chairs',
    'category_Sofas', 'category_Tables',
    'lag_sales_1', 'lag_sales_7', 'lag_sales_14',
    'rolling_mean_sales_7', 'rolling_std_sales_7'
]
X = df[exog_features]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X = pd.DataFrame(X_scaled, columns=exog_features, index=df.index)


split = int(0.8 * len(df))
train_y, test_y = y.iloc[:split], y.iloc[split:]
train_X, test_X = X.iloc[:split], X.iloc[split:]


sarimax_model = SARIMAX(
    train_y,
    exog=train_X,
    order=(1,1,1),
    seasonal_order=(1,1,1,7),
    enforce_stationarity=False,
    enforce_invertibility=False
)

sarimax_result = sarimax_model.fit(disp=False)
print("SARIMAX Training Complete for Sales Forecasting")


pred_y = sarimax_result.predict(
    start=len(train_y),
    end=len(train_y)+len(test_y)-1,
    exog=test_X
)

pred_y = np.expm1(pred_y)
test_y_real = np.expm1(test_y)


mae = mean_absolute_error(test_y_real, pred_y)
rmse = np.sqrt(mean_squared_error(test_y_real, pred_y))
r2 = r2_score(test_y_real, pred_y)
mape = np.mean(np.abs((test_y_real - pred_y) / test_y_real)) * 100

print("\nSARIMAX Model Performance for Sales Forecasting")
print(f"MAE : {mae:.4f}")
print(f"RMSE: {rmse:.4f}")
print(f"R²  : {r2:.4f}")
print(f"MAPE: {mape:.2f}%")


forecast_result = sarimax_result.get_forecast(steps=N, exog=future_exog)
future_mean = np.expm1(forecast_result.predicted_mean)
confidence_intervals = np.expm1(forecast_result.conf_int())

plt.figure(figsize=(14,6))
plt.plot(future_dates, future_mean, label='Forecasted Sales', color='green', marker='o')
plt.fill_between(future_dates,
                 confidence_intervals.iloc[:, 0],
                 confidence_intervals.iloc[:, 1],
                 color='lightgreen', alpha=0.3)
plt.xlabel('Date')
plt.ylabel('Sales Units')
plt.title('Next 15 Days Sales Forecast')
plt.xticks(rotation=45)  
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend()
plt.tight_layout()
plt.show()"""