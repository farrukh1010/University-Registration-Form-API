

from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import BaseModel, EmailStr, validator
from typing import Optional,List
# from typing import List

app = FastAPI()

# Mock database
students_db = {
    1234: {"name": "Farrukh Zaman", " subject": "Computer Science", "grades": {"Fall2024": "A", "Spring2025": "B"}},
    2345: {"name": "Shahzeb", " subject": "Mathematics", "grades": {"Fall2024": "B", "Spring2025": "A"}},
    3456: {"name": "Ahmad Zeb", " subject": "Physics", "grades": {"Fall2024": "A", "Spring2025": "A"}},
}

# class StudentInfo(BaseModel):
#     name: str
#     subject: str
#     grades: Optional[dict] = None
class RegisterStudent(BaseModel):
    name: str
    email: EmailStr
    age: int
    courses: List[str]
    subject: Optional[str] = None
    grades: Optional[dict] = None


@app.get("/students/{student_id}")
async def get_student_info(
    student_id: int = Path(...),
    include_grades: bool = Query(False),
    semester: Optional[str] = Query(None, regex=r"^(Fall|Spring|Summer)\d{4}$")
):
    try:
             # Validate student_id
        if student_id < 1000 or student_id > 9999:
            raise HTTPException(
                status_code=422,
                detail="student_id must be between 1000 and 9999",
                
            )

        # Retrieve student data
        student = students_db.get(student_id)
        if not student:
            # raise ValueError("Student not found")
                raise HTTPException(
                status_code=422,  # Still a validation issue since ID doesn't exist
                detail=f"Student with id {student_id} does not exist"
            )

        # Prepare response
        response = {
            "status": "success",
            "data": {
                "id": student_id,
                "person": student
            }
        }

        # Include grades if requested
        if include_grades:
            if semester:
                grades = {semester: student["grades"].get(semester, "No grade available")}
            else:
                grades = student["grades"]
            response["data"]["person"]["grades"] = grades
        else:
            response["data"]["person"].pop("grades", None)

        return response

    except HTTPException as http_exc:
        # Re-raise HTTP exceptions for FastAPI to handle them
        raise http_exc
    except ValueError as e:
        return {
            "status": "error",
            "message": str(e),
            "data": None
        }
    except Exception as e:
        return {
            "status": "error",
            "message": "An unexpected error occurred.",
            "data": None
        }
    

    
 # Mock database for registered students
registered_students = [
    {
  "name": "Alice Smith",
  "email": "alice@example.com",
  "age": 20,
  "courses": "Mathematics"
}
]

# Request model for registering a student
class RegisterStudent(BaseModel):
    name: str
    email: EmailStr
    age: int
    courses: List[str]

    # Validators
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

@app.post("/students/register")
async def register_student(student: RegisterStudent):
    # Check for duplicate email
    if any(s["email"] == student.email for s in registered_students):
        raise HTTPException(
            status_code=400,
            detail=f"A student with email {student.email} is already registered"
        )

    # Save the student in the mock database
    registered_students.append(student.dict())

    return {
        "status": "success",
        "message": "Student registered successfully",
        "data": student.dict()
    }




 









