# Lab 3 - Stock Market Analysis

## Setup
- Create and active a virtual environment
```bash
virtualenv venv
source venv/bin/activate  # or "venv\Scripts\activate" on Windows
```
- To install the necessary libraries
```bash
cd src
pip install -r requirements.txt
```

## Commands
To run the commands stay in the `src` directory

### User Management
- Create a new user
```bash
python main.py user create --username dan_man --first_name Dan --last_name Mano --password dan_password
```

- Get user Information
```bash
python main.py user get-info --username dan_man --password dan_password
```

### Portfolio Management
- Create a new portfolio
```bash
python main.py portfolio create --username dan_man --password dan_password --portfolio_name my_first_portfolio
```

- List all portfolios
```bash
python main.py portfolio list-all --username john_doe --password secretpassword123
```

- Fetch portfolio by id
```bash
python main.py portfolio fetch-one --username john_doe --password secretpassword123 --portfolio_id 65ba2aee0d0a8a7425f7fe2b
```

- Add a stock to the portfolio
```bash
python main.py portfolio add-stock --username dan_man --password dan_password --portfolio_id 65bb27be57e671a76824d4e6 --ticker_code TSLA
python main.py portfolio add-stock --username dan_man --password dan_password --portfolio_id 65bb27be57e671a76824d4e6 --ticker_code FOXA
python main.py portfolio add-stock --username dan_man --password dan_password --portfolio_id 65bb27be57e671a76824d4e6 --ticker_code NFLX
python main.py portfolio add-stock --username dan_man --password dan_password --portfolio_id 65bb27be57e671a76824d4e6 --ticker_code GM
```

- Remove a stock to the portfolio
```bash
python main.py portfolio remove-stock --username dan_man --password dan_password --portfolio_id 65bb27be57e671a76824d4e6 --ticker_code GM
```

- Fetch portfolio stocks data
```bash
python main.py portfolio fetch-portfolio-data --username john_doe --password secretpassword123 --portfolio_id 65ba0ac4e4178f1bf53babac
```

- Delete a portfolio
```bash
python main.py portfolio remove --username john_doe --password secretpassword123 --portfolio_id 65ba1f98a59d90bf7bb83d98
```

### Fetch Market Data
- Fetch Stock data
```bash
python main.py market-data fetch-stock-data --username john_doe --password secretpassword123 --ticker_code GOOG --start_date 2022-01-01 --end_date 2022-12-31
```

## Author:
- Name: Kayvan Shah
- Email: kpshah@usc.edu
- USC ID: 1106650685
