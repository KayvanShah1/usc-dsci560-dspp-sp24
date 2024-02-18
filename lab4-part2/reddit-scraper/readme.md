# Lab 4 Part 1 - Reddit API Data Extraction

## Important Files
Make sure files are present in to root directory of the project
1. .env - File with environment variables
2. ca.pem - Certifcate Authentication file for database
3. requirements.txt - File with dependencies to installed for the project

## Setup
- For setup move into `reddit-scraper` directory
```bash
cd reddit-scraper
```

- Create and active a virtual environment
```bash
virtualenv venv
source venv/bin/activate  # or "venv\Scripts\activate" on Windows
```
- To install the necessary libraries
```bash
pip install -r requirements.txt
```

## Running the script
- Make sure the all the important files listed above are present at the correct location
- Virtual Environment is created and activated
- To run the script
    - Move into the `/src` directory
    ```bash
    cd src
    ```
    - Run the `main.py` script
    ```bash
    python main.py
    ```
    - To scrape more posts a `line 107` can be modified in the `main.py` file.
    ```py
    new_post_count = <enter your desired number>
    ```
    - Scraping may take some time so please be patient.
- Data Collected is processed and ingested into MySQL database.

## To view the data ingested data MySQL database
- Open `MySQL Workbench`. Use the following environment variables to connect to the database
    - MYSQL_USERNAME
    - MYSQL_PASSWORD
    - MYSQL_HOST

- Snapshot after a successful connection to the database
    ![MySQL DB Snapshot](../docs/mysqldb.jpg)

## Code Files

### crud.py
This program is used to insert information of the scraped posts in bulk to the database.  
The program discards the post if it already exists in the database.

### database.py
This program establishes a connection between python and the SQL server.

### doc2vec.py
The program is used to train a gensim model. 
The gensim model creates embeddings which are used to calculate similarity between documents and them a cluster.

### extract.py
The program cleans and pre-processes the text scraped from the reddit posts as well as the text of the website whose link is mentioned in the post.  
The program also extracts the top 10 keywords that characterizes the document.

### main.py
This is the driver program which is used to scrape the reddit posts from the tech subreddit page every 5 minutes and pre-process and store the data in the database.  
The program also takes a keyword as a user input and returns the documents found similar to the keyword from the appropriate cluster.  

### model.py
The program defines a schema according to which data will be stored in the MySQL server.

### schema.py
The program creates a pydantic model to validate the format of the data before storing it in the database.  

### settings.py
This program is used to set up access to the appropriate certificate and environment credentials required to connect with the MySQL database.

<!-- ## Author:
- Name: Kayvan Shah
- Email: kpshah@usc.edu
- USC ID: 1106650685 -->
