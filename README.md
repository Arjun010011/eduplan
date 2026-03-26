# EduPlan 📚

EduPlan is an AI-powered **Course Plan Generator** for teachers. It accepts course details (board, grade, subject, date range, and optional instructions) and uses an LLM via OpenRouter to automatically generate a structured week-by-week curriculum plan — delivered as a downloadable PDF.

---

## 🏗️ Architecture

```
eduplan/
├── backend/          # Django REST Framework API
│   ├── eduplan/      # Project settings, URLs, exception handler
│   ├── planner/      # Core app: plan generation, PDF rendering
│   └── textbooks/    # Textbook catalog API (CBSE, ICSE, Karnataka)
└── frontend/         # React (Create React App) UI
    └── src/
        ├── api/      # Axios API client
        ├── components/
        └── pages/
```

---

## ✨ Features

- Generate **week-by-week course plans** powered by OpenRouter LLM
- Supports **CBSE, ICSE, and Karnataka State Board**
- PDF export of generated plans
- Textbook catalog with filtering by board, grade, subject, and language
- Health-check endpoint

---

## 🛠️ Tech Stack

| Layer     | Technology                              |
|-----------|-----------------------------------------|
| Frontend  | React 18, React Router v6, Axios        |
| Backend   | Django 4.2+, Django REST Framework 3.14+|
| Database  | SQLite (file-based, zero config)        |
| AI        | OpenRouter API (LLM gateway)            |
| PDF       | ReportLab                               |
| Scraping  | Requests + BeautifulSoup4               |

---

## ⚙️ Prerequisites

- Python 3.10+
- Node.js 18+ & npm

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/eduplan.git
cd eduplan
```

---

### 2. Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create your environment file
cp .env.example .env
```

Edit `.env` and fill in your values:

```env
SECRET_KEY=your-django-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_PATH=db.sqlite3

# Get your key at https://openrouter.ai
OPENROUTER_API_KEY=sk-or-your-key-here
OPENROUTER_MODEL=openrouter/free        # or any model slug from openrouter.ai
OPENROUTER_SITE_URL=http://localhost:3000
OPENROUTER_APP_NAME=eduplan-backend
```

> **Tip:** Generate a Django `SECRET_KEY` with:
> ```bash
> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

```bash
# Apply database migrations
python manage.py migrate

# (Optional) Create an admin superuser
python manage.py createsuperuser

# Start the backend server
python manage.py runserver
```

The API will be available at **http://localhost:8000**.

---

### 3. Frontend Setup

```bash
cd ../frontend

# Install Node dependencies (already done if node_modules/ exists)
npm install

# Start the React development server
npm start
```

The app will open at **http://localhost:3000**. The frontend proxies all `/api/*` requests to the backend on port 8000.

---

## 🔌 API Endpoints

| Method | Endpoint                     | Description                          |
|--------|------------------------------|--------------------------------------|
| GET    | `/api/health/`               | Health check (also checks pdflatex)  |
| POST   | `/api/planner/generate/`     | Generate a course plan PDF           |
| GET    | `/api/textbooks/`            | List textbooks (supports filtering)  |
| GET    | `/api/textbooks/{id}/`       | Retrieve a single textbook           |

### Generate Plan — Request Body

```json
{
  "teacher_name": "Ms. Anjali Rao",
  "board": "CBSE",
  "grade": 8,
  "subject": "Mathematics",
  "start_date": "2025-06-01",
  "end_date": "2025-03-31",
  "instructions": "Focus on NCERT exercises. Include formative assessments every 4 weeks."
}
```

### Textbook Filters

`GET /api/textbooks/?board=CBSE&grade=8&subject=Mathematics&language=English`

---

## 🗄️ Database

SQLite is used by default — no configuration required. The database file is created at the path specified by `DB_PATH` in your `.env` (defaults to `db.sqlite3` inside the `backend/` directory).

---

## 📁 Environment Variables Reference

| Variable               | Required | Default              | Description                          |
|------------------------|----------|----------------------|--------------------------------------|
| `SECRET_KEY`           | ✅       | —                    | Django secret key                    |
| `DEBUG`                | ❌       | `True`               | Enable Django debug mode             |
| `ALLOWED_HOSTS`        | ❌       | `localhost`          | Comma-separated list of allowed hosts|
| `DB_PATH`              | ❌       | `db.sqlite3`         | Path to SQLite database file         |
| `OPENROUTER_API_KEY`   | ✅       | —                    | Your OpenRouter API key              |
| `OPENROUTER_MODEL`     | ❌       | `openrouter/free`    | Model slug from openrouter.ai        |
| `OPENROUTER_SITE_URL`  | ❌       | `""`                 | Your site URL (shown in OpenRouter)  |
| `OPENROUTER_APP_NAME`  | ❌       | `eduplan-backend`    | App name shown in OpenRouter         |

---

## 🧩 Django Admin

Access the admin panel at **http://localhost:8000/admin/** after creating a superuser:

```bash
python manage.py createsuperuser
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/your-feature`)
3. Commit your changes (`git commit -m "feat: add your feature"`)
4. Push and open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.
