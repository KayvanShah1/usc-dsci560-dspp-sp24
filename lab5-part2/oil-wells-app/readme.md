## Lab 5 Part 2 - Oil Wells Analysis and Visualization

### Important Files and Folders
1. **`oil-wells-app/.env`**: File with environment variables.
2. **`oil-wells-app/requirements.txt`**: File with dependencies to be installed for the project.
3. **`oil-wells-app/`**: Directory containing the source code for the web app.
4. **`docs/`**: Documentation including meeting minutes and README in PDF format.
5. **`notebooks/`**: Experimental usage and testing of concepts.

### Setup

1. Navigate to the `oil-wells-app` directory:
   ```bash
   cd oil-wells-app
   ```

2. Create and activate a virtual environment:
   ```bash
   virtualenv venv
   source venv/bin/activate  # or "venv\Scripts\activate" on Windows
   ```

3. Install the necessary libraries:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Web Application

1. Ensure that:
   - All the important files and folders listed above are present at the correct location.
   - The virtual environment is created and activated.

2. To run the script:
   - Ensure you are in the `/oil-wells-app` directory:
     ```bash
     cd oil-wells-app
     ```
   - Start the web app:
     ```bash
     uvicorn app.main:app 
     ```

### About Python Files

| File Name    | Purpose                                                                                                   |
|--------------|-----------------------------------------------------------------------------------------------------------|
| `crud.py`    | This file contains function definitions responsible for querying and processing oil wells data.           |
| `database.py`| In this file, a connection is established between Python and the SQL server. It contains code to handle database connections, execute SQL queries, and manage transactions.  |
| `main.py`    | Entry point for the FastAPI web application, handling basic routing and middleware configurations. It serves the home page with the oil wells analysis and visualization, and redirects any incorrect routes to the home page for a seamless user experience. |
| `mapgen.py`  | This module creates a Folium map by processing well data and converting it into GeoJSON format. It performs format conversion on the well data to generate a GeoJSON representation suitable for mapping. The module then plots markers on the map, along with tooltips and popups to provide additional information about each well. Finally, it returns an HTML representation of the map embedded in the generated webpage. |
| `model.py`   | In this file, the schema for data storage in the MySQL server is defined. It includes the structure of database tables and models, and it creates these tables if they do not already exist in the database. |
| `schema.py`  |  This file defines Pydantic models, which are used for data validation and format conversion. Pydantic models ensure that the data sent to and received from the API endpoints conforms to a specified schema. |
| `settings.py`| Here, environment credentials required for connecting to the MySQL database is set up. It handles configuration settings and environment variables used throughout the application. |