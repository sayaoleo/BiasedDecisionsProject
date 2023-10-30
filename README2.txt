- Instructions for Setting Up and Running the ABI Tool from Eduardo Ramos

This guide outlines the steps to configure and run the project on your computer.

- Step 1: Create a Folder

1. Create a new folder on your computer to store the project files located in the GitHub repository

- Step 2: Set Up Database Access

1. Inside the project folder, create a new folder called `.streamlit`.

2. Within the `.streamlit` folder, create a file named `secrets.toml`.

3. Add the following information to the `secrets.toml` file to connect to a PostgreSQL database:

[postgres]
dbname = "postgres"
user = "postgres"
password = "yourpassword"
host = "localhost"
port = 5432
schema_name = "finalexperiment"


Make sure to replace `"yourpassword"` with your database password and `"finalexperiment"` with your schema name.

- Step 3: Install Streamlit and other Modules

1. Open the terminal or command prompt on your system.

2. Enter the following code:

pip install streamlit

pip install peewee

streamlit hello

- Step 4: Install pgAdmin4

1. Download and install pgAdmin4 on your computer. This is the tool used, but you can choose another database management tool if you prefer.

- Step 5: Create the Table in the Database

1. Open pgAdmin4 and access the "Query Tool."

2. Execute the SQL code in the file "BDCode.txt" to create a table in the database:

- Step 6: Run the Project
1. Open the terminal or command prompt on your system.

2. Navigate to the project folder using the cd command, for example:

cd "path to your folder"

streamlit run app.py


