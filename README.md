# EHTMS Tasks Application

A production-ready task management backend built with **FastAPI**, **PostgreSQL**, **JWT Authentication**, and **SQLAlchemy**.
This project demonstrates modern backend engineering practices including authentication, modular architecture, RESTful APIs, database relationships, Docker support, and scalable project structure.

---

## 🚀 Features

* 🔐 JWT Authentication & Authorization
* 👤 User Registration & Login
* ✅ Task CRUD Operations
* 📌 Task Status Management
* 🗄 PostgreSQL Database Integration
* ⚡ FastAPI Async API Architecture
* 📦 Pydantic Validation
* 🐳 Docker Support
* 📖 Interactive API Documentation
* 🧩 Modular Scalable Project Structure
* 🔒 Environment Variable Configuration

---

## 🛠 Tech Stack

| Technology  | Purpose          |
| ----------- | ---------------- |
| Python 3.12 | Backend Language |
| FastAPI     | Web Framework    |
| PostgreSQL  | Database         |
| SQLAlchemy  | ORM              |
| Pydantic    | Data Validation  |
| JWT         | Authentication   |
| Docker      | Containerization |
| Uvicorn     | ASGI Server      |

---

# 📁 Project Structure

```bash
ehtms_tasks_application/
│
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── auth.py
│   │           └── tasks.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   └── task.py
│   │
│   ├── schemas/
│   │   ├── user.py
│   │   └── task.py
│   │
│   ├── services/
│   │   └── database.py
│   │
│   └── main.py
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
└── README.md
```

---

# ⚙️ Installation

## 1️⃣ Clone Repository

```bash
git clone https://github.com/omi1811/ehtms_tasks_application.git

cd ehtms_tasks_application
```

---

## 2️⃣ Create Virtual Environment

### Windows

```bash
python -m venv .venv

.venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv .venv

source .venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install --upgrade pip

pip install -r requirements.txt
```

---

# 🗄 Database Setup

Make sure PostgreSQL is running.

Create database:

```sql
CREATE DATABASE ehtms_db;
```

---

# 🔐 Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql://ehtms_user:ehtms_password_123@localhost:5432/ehtms_db

SECRET_KEY=your_secret_key

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

# ▶️ Run Application

```bash
uvicorn app.main:app --reload
```

Server runs at:

```bash
http://127.0.0.1:8000
```

---

# 📖 API Documentation

FastAPI automatically generates docs.

## Swagger UI

```bash
http://127.0.0.1:8000/docs
```

## ReDoc

```bash
http://127.0.0.1:8000/redoc
```

---

# 🔑 Authentication Flow

## Register User

```http
POST /api/v1/auth/register
```

## Login

```http
POST /api/v1/auth/login
```

Returns:

```json
{
  "access_token": "JWT_TOKEN",
  "token_type": "bearer"
}
```

Use token in Swagger Authorize button:

```bash
Bearer YOUR_TOKEN
```

---

# ✅ Task Endpoints

| Method | Endpoint               | Description        |
| ------ | ---------------------- | ------------------ |
| POST   | `/tasks/`              | Create Task        |
| GET    | `/tasks/`              | Get All Tasks      |
| GET    | `/tasks/{id}`          | Get Single Task    |
| PUT    | `/tasks/{id}`          | Update Task        |
| DELETE | `/tasks/{id}`          | Delete Task        |
| PATCH  | `/tasks/{id}/complete` | Mark Task Complete |

---

# 🐳 Docker Setup

## Build Containers

```bash
docker compose build
```

## Start Containers

```bash
docker compose up
```

## Run in Detached Mode

```bash
docker compose up -d
```

---

# 🧪 Example API Request

## Create Task

```json
{
  "title": "Complete FastAPI Project",
  "description": "Finish backend APIs",
  "status": "pending"
}
```

---

# 🔒 Security Features

* Password Hashing
* JWT Token Authentication
* Protected Routes
* Input Validation
* Environment Variable Isolation

---

# 📌 Learning Goals of This Project

This project helps practice:

* FastAPI Backend Development
* Authentication Systems
* REST API Design
* Database Modeling
* SQLAlchemy ORM
* Docker Fundamentals
* Production-style Backend Architecture

---

# 🚀 Future Improvements

* Role-Based Access Control (RBAC)
* Redis Caching
* Background Tasks
* Email Notifications
* Task Deadlines & Priorities
* Pagination & Filtering
* Unit & Integration Testing
* CI/CD Pipeline
* Kubernetes Deployment

---

# 👨‍💻 Author

Made by Omkar Shrotri

GitHub: [omi1811 GitHub Profile](https://github.com/omi1811?utm_source=chatgpt.com)

Repository: [EHTMS Tasks Application](https://github.com/omi1811/ehtms_tasks_application?utm_source=chatgpt.com)

---

# 📄 License

This project is licensed under the MIT License.

---

# ⭐ Support

If you found this project helpful:

* ⭐ Star the repository
* 🍴 Fork the project
* 🛠 Contribute improvements

Happy Coding 🚀
