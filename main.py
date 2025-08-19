# ------------------ IMPORTS ------------------

# 'from ... import ...' means: bring something specific from a library
from fastapi import FastAPI                      # FastAPI framework for building APIs
from fastapi.middleware.cors import CORSMiddleware  # Middleware to handle CORS
import psycopg                                   # Library for connecting to PostgreSQL databases


# ------------------ CREATE APP ------------------

# 'app = FastAPI()' creates an API application object
# This object is our "server" where we will define routes (endpoints)
app = FastAPI()


# ------------------ CORS SETUP ------------------

# 'origins' is a Python list [] containing allowed frontend addresses
# Only these addresses can send requests to this API
origins = [
    "http://127.0.0.1:5500"   # local frontend (e.g., HTML/JS running in browser)
]

# Add CORS middleware to the app
# Middleware = software that sits between the app and the user requests
app.add_middleware(
    CORSMiddleware,           # The middleware class we are adding
    allow_origins=origins,    # Only allow requests from the given origins list
    allow_credentials=True,   # Allow cookies, tokens, or login info to be sent
    allow_methods=["*"],      # "*" means all HTTP methods are allowed (GET, POST, PUT, DELETE...)
    allow_headers=["*"],      # "*" means allow any headers (extra request info)
)


# ------------------ DATABASE CONNECTION ------------------

# Define a function called 'get_connection' that connects to PostgreSQL
def get_connection():
    return psycopg.connect(   # psycopg.connect() opens a connection to the database
        dbname="school_db",   # Name of the database
        user="allano",        # Username
        password="Allan1997!",# Password
        host="localhost",     # Where the database is running ("localhost" = same computer)
        port="5432"           # Port number for PostgreSQL
    )


# ------------------ ROUTES ------------------

# A "route" is a URL path where people can access your API

# -------- Home Route --------
@app.get("/")   # '@app.get("/")' means: when someone visits "/" using GET method, run the function below
def home():     # Function name is 'home'
    # return sends a response in JSON format (dictionary in Python automatically becomes JSON)
    return {"message": "Welcome to the Student API"}


# -------- Get Students Route --------
@app.get("/students")   # When someone visits "/students" with GET method, run this function
def get_students():     # Function name is 'get_students'
    # 'with' automatically handles opening and closing the database connection
    with get_connection() as conn:   # Open a connection to the database
        # Open a cursor (tool to run SQL commands)
        # row_factory=psycopg.rows.dict_row makes rows look like dictionaries
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            # Run an SQL command
            cur.execute("SELECT * FROM students;")
            # Fetch all rows from the result
            students = cur.fetchall()
    # Send the result back as JSON
    return {"students": students}
