



from fastapi import FastAPI, HTTPException, Query, Path, Request
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict
import time
import random

app = FastAPI()

# In-memory database
students_db: Dict[int, dict] = {
    1234: {"name": "Farrukh Zaman", "subject": "Computer Science", "grades": {"Fall2024": "A", "Spring2025": "B"}},
    2345: {"name": "Shahzeb", "subject": "Mathematics", "grades": {"Fall2024": "B", "Spring2025": "A"}},
    3456: {"name": "Ahmad Zeb", "subject": "Physics", "grades": {"Fall2024": "A", "Spring2025": "A"}},
}

# Middleware to log requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    method = request.method
    url = request.url
    client = request.client.host

    response = await call_next(request)

    process_time = time.time() - start_time
    print(f"[{client}] {method} {url} - {response.status_code} - {process_time:.2f}s")

    return response


# Models
class RegisterStudent(BaseModel):
    name: str
    email: EmailStr
    age: int
    courses: List[str]

    @validator("name")
    def validate_name(cls, name):
        if not name.replace(" ", "").isalpha():
            raise ValueError("Name must contain only alphabets and spaces")
        if len(name) < 1 or len(name) > 50:
            raise ValueError("Name must be between 1 and 50 characters")
        return name

    @validator("age")
    def validate_age(cls, age):
        if age < 18 or age > 30:
            raise ValueError("Age must be between 18 and 30")
        return age

    @validator("courses", pre=True, always=True)
    def validate_courses(cls, courses):
        if not isinstance(courses, list):
            raise ValueError("Courses must be a list of strings")
        if len(courses) < 1 or len(courses) > 5:
            raise ValueError("There must be between 1 and 5 courses")
        if len(set(courses)) != len(courses):
            raise ValueError("Duplicate course names are not allowed")
        for course in courses:
            if not isinstance(course, str):
                raise ValueError("Each course name must be a string")
            if len(course) < 5 or len(course) > 30:
                raise ValueError("Each course name must be between 5 and 30 characters")
        return courses


class UpdateEmailRequest(BaseModel):
    email: EmailStr

    class Config:
        schema_extra = {
            "example": {
                "email": "new.email@example.com"
            }
        }


# Routes
@app.get("/")
def read_root():
    return {"University Registration Form API": "Welcome to the University Registration Form API"}
@app.get("/students/{student_id}", summary="Get Student Info", description="Retrieve student information by ID.")
async def get_student_info(
    student_id: int = Path(..., ge=1000, le=9999),
    include_grades: bool = Query(False),
    semester: Optional[str] = Query(None, regex=r"^(Fall|Spring|Summer)\d{4}$")
):
    student = students_db.get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")

    response = {
        "status": "success",
        "data": {"id": student_id, "person": student}
    }

    if include_grades:
        if semester:
            grades = {semester: student["grades"].get(semester, "No grade available")}
        else:
            grades = student["grades"]
        response["data"]["person"]["grades"] = grades
    else:
        response["data"]["person"].pop("grades", None)

    return response


@app.post("/students", summary="Add Student", description="Adds a new student to the in-memory database.")
async def add_student(student: RegisterStudent):
    while True:
        student_id = random.randint(1000, 9999)
        if student_id not in students_db:
            break

    students_db[student_id] = student.dict()
    return {
        "status": "success",
        "message": f"Student added with ID {student_id}",
        "data": {
            "id": student_id,
            **student.dict()
        }
    }


@app.post("/students/register", summary="Register Student", description="Registers a new student.")
async def register_student(student: RegisterStudent):
    if any(s.get("email") == student.email for s in students_db.values()):
        raise HTTPException(status_code=400, detail=f"A student with email {student.email} is already registered")

    student_id = random.randint(1000, 9999)
    students_db[student_id] = student.dict()
    return {
        "status": "success",
        "message": f"Student registered with ID {student_id}",
        "data": {
            "id": student_id,
            **student.dict()
        }
    }


@app.put("/students/{student_id}/email", summary="Update Student Email", description="Updates a student's email by ID.")
async def update_student_email(
    student_id: int = Path(..., ge=1000, le=9999),
    email_request: UpdateEmailRequest = None
):
    student = students_db.get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")

    student["email"] = email_request.email
    return {
        "status": "success",
        "message": f"Email updated for student ID {student_id}",
        "data": {
            "id": student_id,
            "updated_email": email_request.email
        }
    }










