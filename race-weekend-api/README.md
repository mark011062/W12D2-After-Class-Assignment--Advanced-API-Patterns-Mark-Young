# Race Weekend Checklist Manager API

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_



Advanced API Patterns – Production-Ready REST API



Overview



This project is a production-ready REST API built for the Advanced API Patterns assignment. The API models a race weekend checklist manager for motorcycle racing teams, allowing authenticated users to manage race events and tasks while enforcing security, rate limiting, and best-practice API design patterns.



The system demonstrates real-world backend architecture, including JWT authentication, role-based access control, dependency injection, rate limiting, and automated testing with coverage enforcement.



Features

Authentication \& Authorization



User registration and login



Secure password hashing (bcrypt)



JWT-based authentication



Role-based access control:



Users manage their assigned tasks



Admins create events and assign tasks



Race Events



Admin-only creation of race weekend events



Events include track, location, and event date



Tasks



Tasks belong to race events



Tasks can be assigned to specific users



Users can:



View assigned tasks



Update completion status



Delete their own tasks



Rate Limiting



Redis-backed rate limiting on task endpoints



Standard rate-limit response headers:



X-RateLimit-Limit



X-RateLimit-Remaining



X-RateLimit-Reset



Redis is fully mocked in tests



Testing



Pytest test suite



SQLite test database



Dependency overrides for database and Redis



Coverage enforcement (--cov-fail-under=80)



Tech Stack



Python 3.12



FastAPI



SQLAlchemy



SQLite (tests)



JWT (PyJWT)



Passlib + bcrypt



Redis (rate limiting)



pytest + pytest-cov



Project Structure

app/

├── api/v1/        # Route handlers

├── core/          # Security, config, rate limiting

├── db/            # Database models and session

├── exceptions/    # Centralized error handling

├── middleware/    # Request middleware

├── schemas/       # Pydantic schemas

├── seed.py

└── main.py



tests/

├── conftest.py

├── test\_auth.py

├── test\_rate\_limit.py

├── test\_tasks.py

├── test\_tasks\_more\_coverage.py

└── test\_health.py



API Endpoints (Summary)

Auth



POST /v1/auth/register



POST /v1/auth/login



Health



GET /v1/health



GET /v1/health/ready



Events (Admin Only)



POST /v1/events



Tasks



GET /v1/tasks



GET /v1/tasks/{id}



POST /v1/tasks



PATCH /v1/tasks/{id}



DELETE /v1/tasks/{id}



Running the Application

python -m venv venv

venv\\Scripts\\activate

pip install -r requirements.txt

uvicorn app.main:app --reload





API available at:



http://localhost:8000





Swagger docs:



http://localhost:8000/docs



Running Tests

python -m pytest -q





With coverage:



python -m pytest -q --cov=app --cov-report=term-missing --cov-fail-under=80

