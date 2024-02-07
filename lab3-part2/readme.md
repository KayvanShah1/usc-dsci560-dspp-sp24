# Lab 3 Part 2

## Model 1: Simple Moving Average (SMA)

### Input
- **Data Files:** CSV files containing historical stock data. Each file should contain Date, Open, High, Low, Close, Adj Close, and Volume columns.
  - Filenames: `ANDANIENT.NS.csv`, `META.csv`, `AAPL.csv` (can be modified inside the script)
- **Stock Names:** List of stock symbols corresponding to the data files such as 'ANDANIENT', 'META', 'APPLE'. (can be modified inside the script)

### Execution
```
python lab3_sma.py
```

### Dependencies
- Python 3.x
- pandas
- matplotlib
- numpy

### About

**Data Loading and Preparation:**
- The mock trading environment begins by loading historical price data for multiple stocks from CSV files. Each CSV file contains columns such as Date, Open, High, Low, Close, and Volume.
- The data is then processed and prepared for analysis. This includes converting date columns to DateTime objects, setting the date column as the index, and sorting the DataFrame by date.

**Trading Strategy:**
- The trading strategy is implemented through the `generate_signals()` function. This function generates buy and sell signals based on predefined conditions using moving averages (SMA) and the Relative Strength Index (RSI).
- Buy signals are generated when certain conditions, such as SMA crossing a threshold and RSI falling below a certain level, are met. Sell signals are generated similarly based on opposite conditions.
- The trading strategy aims to capture potential trends and reversals in stock prices.

**Mock Trading Simulation:**
- The `mock_trading()` function simulates trading based on the generated buy and sell signals. It inputs an initial fund and iterates through each data point, executing trades accordingly.
- When a buy signal is generated, the strategy buys as many shares as possible with the available cash. Conversely, when a sell signal is generated, the strategy sells all the shares it holds. The portfolio value is tracked over time, considering changes in cash and the value of shares held.

**Portfolio Management:**
- The mock trading environment manages multiple portfolios, each corresponding to a different stock. Portfolios are represented as dictionaries, where the key is the stock symbol, and the value is the final portfolio value.
- Additionally, annualized returns and Sharpe ratios are calculated for each portfolio to evaluate performance.

**Visualization:**
- Price charts with buy and sell signals are generated using Matplotlib, allowing users to visualize the trading strategy's performance.
- Each chart displays the stock's closing price over time and markers indicating buy and sell signals.

### Functions
- `calculate_sma`: Calculates the Simple Moving Average for a given window size.
- `calculate_rsi`: Calculates the Relative Strength Index for a given window size.
- `generate_signals`: Generates buy and sell signals based on SMA and RSI.
- `calculate_annualized_returns`: Calculates the annualized returns of the portfolio.
- `calculate_sharpe_ratio`: Calculates the Sharpe ratio of the portfolio.
- `mock_trading`: Simulates trading based on generated signals and calculates portfolio value.

### Output
- The script generates plots showing the stock's closing prices and buy and sell signals.
- Transaction log indicating buy and sell actions and the number of shares and prices.
- Performance Metrics:
  - Final portfolio value for each stock.
  - Annualized returns for each stock.
  - Sharpe ratio for each stock.
  - Overall portfolio value and profit.

---

## Model 2: Long Short-Term Memory (LSTM)

### Input Parameters
- **Ticker code:** Ticker of the company whose stocks will be scraped from the Yahoo Finance website.

### Output
- A data frame consisting of the closing prices, including the forecasted prices for the next 14 days.

### Execution command
```
python apple_inc_(aapl)_stock_price_forecast_lstm.py <ticker code>
```

---

## Model 3: Autoregressive Integrated Moving Average (ARIMA)

### Dependencies
- Python 3.x
- pandas
- matplotlib
- seaborn
- statsmodels
- pmdarima
- Scikit-learn

### Input
- **CSV File:** The input data is provided in a CSV file (`ANDANIENT.NS.csv`) containing historical stock price data. The CSV file should have columns such as Date, Open, High, Low, Close, Adjusted Close, and Volume.

### Output
- **Forecasted Stock Prices:** The script generates forecasted stock prices using the ARIMA model. It predicts future stock prices based on historical data and model parameters.
- **Plot:** The script visualizes the actual and predicted stock prices over time. It also displays confidence intervals around the forecasted values.
- **Evaluation Metrics:** The script calculates and prints evaluation metrics such as Mean Squared Error (MSE), Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and Mean Absolute Percentage Error (MAPE). These metrics quantify the accuracy of the predictions.

### Execution
```
python ARIMA.py
```

### Review
- The script will analyze the historical stock price data, train the ARIMA model, make predictions, and display the results.
- Review the output to assess the predictions' accuracy and the model's performance.

---

**Note:** For more information on how to use each model and its respective scripts, refer to the detailed instructions provided above.