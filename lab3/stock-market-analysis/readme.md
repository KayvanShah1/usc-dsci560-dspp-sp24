# Lab 3 - Stock Market Analysis

## Setup
- Create and active a virtual environment
```bash
virtualenv venv
source venv/bin/activate  # or "venv\Scripts\activate" on Windows
```
- To install the necessary libraries
```bash
pip install -r requirements.txt
```
- Create `.env` at the same level as `/src` directory. Add the follwing environment variables
```bash
MONGODB_URI=<your_cluster_uri>
```

## Command line help
### Entry point
```bash
$ python main.py --help
usage: main.py [-h] {user,portfolio,market-data} ...

Command-line interface for Stock Market Analysis Application

positional arguments:
  {user,portfolio,market-data}
                        Available commands
    user                User management commands
    portfolio           Portfolio management commands
    market-data         Fetch market data commands

options:
  -h, --help            show this help message and exit
```

### User Management
```bash
$ python main.py user --help
usage: main.py user [-h] {create,get-info} ...

positional arguments:
  {create,get-info}  Available user management subcommands
    create           Create a new user
    get-info         Get user information

options:
  -h, --help         show this help message and exit
```

### Portfolio Management
```bash
$ python main.py portfolio --help
usage: main.py portfolio [-h] {create,remove,list-all,fetch-one,add-stock,remove-stock,fetch-portfolio-data} ...

positional arguments:
  {create,remove,list-all,fetch-one,add-stock,remove-stock,fetch-portfolio-data}
                        Available subcommands
    create              Create a new portfolio
    remove              Remove a portfolio
    list-all            List all stock portfolios for a user
    fetch-one           Fetch one stock portfolio information by id
    add-stock           Add a stock to a portfolio
    remove-stock        Remove a stock from a portfolio
    fetch-portfolio-data
                        Fetch stocks data for a portfolio by id

options:
  -h, --help            show this help message and exit
```

### Market Data
```bash
$ python main.py market-data --help
usage: main.py market-data [-h] {fetch-stock-data} ...

positional arguments:
  {fetch-stock-data}  Available subcommands
    fetch-stock-data  Add a stock to a portfolio

options:
  -h, --help          show this help message and exit
```

### For usage of individual commands
```bash
python main.py <command> <subcommand> --help
```

## Example usage
To run the commands stay in the `src` directory

### Directions
- Below commands are run while testing some data may or may not be available so you may recieve an error. It recommended that you start fresh 
    - Creating a new user
        - Get your user info
    - Create a portfolio for the user
        - List all the portfolio of the user to get the portfolio id
        - Retrieve info about the portfolio using that id
    - Add a few stocks to the portfolio
        - To find the stock symbols go to the `Yahoo Finance Website` and search for the symbol
    - Fetch all the data for the stocks
    - Remove a stock
    - Again retrive your portfolio by id
    - Remove your portfolio
    - Now try fetching data for a stock wihout user verification using `market-data` command

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
