import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt

#  Load & preprocess data
df = pd.read_csv("processed_demand_data.csv")
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date')
df.set_index('date', inplace=True)

#  Aggregate daily sales and exogenous variables
daily_sales = df['sales_units'].resample('D').sum()
exog = df[['competitor_price_index', 'promotion_applied']].resample('D').sum()  # Ensure same time index

#  Train-test split for backtesting (simulate forecasting past known data)
train_end = -7  # Last 7 days as test
train_sales = daily_sales[:train_end]
train_exog = exog[:train_end]

test_sales = daily_sales[train_end:]
test_exog = exog[train_end:]

#  Train ARIMAX Model
model = SARIMAX(train_sales, exog=train_exog, order=(5, 1, 0))
fitted_model = model.fit(disp=False)

#  Forecast next 7 days (the test period)
forecast = fitted_model.forecast(steps=7, exog=test_exog)

#  Compute accuracy metrics
mae = mean_absolute_error(test_sales, forecast)
mse = mean_squared_error(test_sales, forecast)
rmse = np.sqrt(mse)
mape = np.mean(np.abs((test_sales - forecast) / test_sales)) * 100

print("🔥 Backtest Accuracy Metrics:")
print(f"MAE: {mae:.2f}")
print(f"MSE: {mse:.2f}")
print(f"RMSE: {rmse:.2f}")
print(f"MAPE: {mape:.2f}%")

#  Plot the results
plt.figure(figsize=(12, 6))
plt.plot(daily_sales, label='Historical Sales Units', color='blue')
plt.plot(forecast.index, forecast.values, label='Forecasted Sales Units (Backtest)', marker='o', color='orange')
plt.xlabel('Date')
plt.ylabel('Sales Units')
plt.title('📈 ARIMAX Backtest Forecast vs Actual')
plt.legend()
plt.grid(True)
plt.show()
