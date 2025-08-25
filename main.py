# 📌 Importing necessary libraries and modules

from fastapi import FastAPI, HTTPException
# FastAPI → the main framework we are using to build APIs (like a web service).
# HTTPException → used to send back an error response if something goes wrong
# (example: if database fails, we return a "500 error" message).

from fastapi.middleware.cors import CORSMiddleware
# CORS (Cross-Origin Resource Sharing) → a rule that controls
# which websites can access your backend API.
# Example: your frontend (HTML/JS) running at http://127.0.0.1:5500
# should be allowed to call this FastAPI backend.

from pydantic import BaseModel
# Pydantic → helps us define and check the structure of incoming data.
# Example: when we add a new student, we expect their details in a specific format.
# BaseModel lets us enforce this structure.

import psycopg
# psycopg → library to connect Python with PostgreSQL database.
# It allows us to run SQL queries like SELECT, INSERT, UPDATE, DELETE.

# ---------------------------------------------------------------

# 📌 Create an instance of FastAPI
app = FastAPI()
# 'app' is the main application object that will hold all our routes (endpoints).

# ---------------------------------------------------------------

# 📌 Allow specific frontend origins (websites) to access the API
origins = ["http://127.0.0.1:5500"]
# This means: only requests coming from this address will be allowed to talk
# to our backend (important for security).

# Add CORS settings to our FastAPI app
app.add_middleware(
    CORSMiddleware,                # Attach CORS middleware
    allow_origins=origins,         # Allow only the frontend running on 127.0.0.1:5500
    allow_credentials=True,        # Allow cookies/authentication info to be shared
    allow_methods=["*"],           # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],           # Allow all headers in the request
)

# ---------------------------------------------------------------

# ✅ Function to connect to the PostgreSQL database
def get_connection():
    return psycopg.connect(
        dbname="school_db",         # Database name (must exist in PostgreSQL)
        user="allano",              # Database username
        password="Allan1997!",      # Database password (⚠️ should be kept secret)
        host="localhost",           # Database server (localhost = running on same computer)
        port="5432"                 # Default PostgreSQL port
    )

# ---------------------------------------------------------------

# ✅ Define a Student model using Pydantic
class Student(BaseModel):
    name: str              # Student's full name
    admission_number: str  # Admission/registration number
    class_name: str        # Class name (we use class_name because 'class' is a reserved word in Python)
    stream: str            # Stream (like North, South, East, West)

# ---------------------------------------------------------------

# 📌 Route: GET /students → Fetch all students
@app.get("/students")
def get_students():
    try:
        # Step 1: Open a connection to the database
        with get_connection() as conn:
            # Step 2: Create a cursor to interact with the database
            # row_factory=psycopg.rows.dict_row → returns results as dictionaries (easy to work with)
            with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
                # Step 3: Run a SQL query to get all students
                cur.execute("SELECT * FROM students;")
                # Step 4: Fetch all rows from the result
                rows = cur.fetchall()
                # Step 5: Convert each row into a dictionary
                students = [dict(row) for row in rows]

        # Step 6: Return the students as JSON to the frontend
        return {"students": students}

    except Exception as e:
        # If something goes wrong (e.g., database error), return a 500 error
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# ---------------------------------------------------------------

# 📌 Route: POST /students → Add a new student
@app.post("/students")
def add_student(student: Student):  # The "student" parameter automatically checks input using our Student model
    try:
        # Step 1: Open a connection to the database
        with get_connection() as conn:
            # Step 2: Create a cursor
            with conn.cursor() as cur:
                # Step 3: Run an INSERT query to add the student
                cur.execute(
                    """
                    INSERT INTO students (name, admission_number, class, stream)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (student.name, student.admission_number, student.class_name, student.stream)
                )
                # Step 4: Fetch the ID of the newly added student
                new_id = cur.fetchone()[0]
                # Step 5: Save (commit) changes to the database
                conn.commit()

        # Step 6: Return a success message with the new student ID
        return {"message": "Student added successfully", "id": new_id}

    except Exception as e:
        # If something goes wrong, return an error message
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
