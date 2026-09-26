<div align="center">

# 🎓 EWU Server

**Scrapes East West University's public websites every week and serves the data through a read-only REST API.**

[![Weekly EWU Data Update](https://github.com/SamirHossain2001/ewu-server-v3/actions/workflows/weekly_update.yml/badge.svg)](https://github.com/SamirHossain2001/ewu-server-v3/actions/workflows/weekly_update.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Supabase](https://img.shields.io/badge/Supabase-3FCF8E?logo=supabase&logoColor=white)](https://supabase.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[**Live API docs**](https://ewu-server.onrender.com/docs) · [Report a bug](https://github.com/SamirHossain2001/ewu-server-v3/issues)

</div>

---

## 📖 Overview

East West University (EWU) publishes a lot of useful information across many web pages: tuition fees, notices, faculty, the academic calendar, clubs, scholarships, policies and more. **EWU Server** collects it into one clean database and exposes it as JSON, so you can build apps, bots or dashboards without scraping the site yourself.

The project has two parts that share one [Supabase](https://supabase.com/) (PostgreSQL) database:

1. **Scraper pipeline** (`main.py`): fetches the EWU websites, detects what changed and safely syncs it to the database. It runs automatically every week on GitHub Actions.
2. **REST API** (`api/`): a read-only [FastAPI](https://fastapi.tiangolo.com/) service that serves the data. It is deployed on Render.

```
  ewubd.edu / admission.ewubd.edu
               │
               ▼
     ┌───────────────────┐      data/current/*.json  (local snapshot)
     │  21 scrapers       │ ───► logs/               (daily log files)
     │  (main.py)         │
     └─────────┬─────────┘
               │  diff check + 30% safety threshold
               ▼
     ┌───────────────────┐        ┌──────────────────┐
     │  Supabase          │ ◄───── │  FastAPI (api/)   │ ◄──── your app / bot / curl
     │  (PostgreSQL + RLS)│  read  │  read-only GET    │
     └───────────────────┘        └──────────────────┘
               │
               └──► Discord webhook (run summary)
```

## ✨ Features

- **21 scrapers**: tuition fees, scholarships, notices, events, clubs, faculty, newsletters, admission deadlines, helpdesk contacts, governance bodies, the academic calendar and 9 university documents (rules, grading, policies, payment, facilities and more).
- **Safe syncing**: every run is compared against the database first. If more than **30%** of a table would change, the update is skipped, which protects you from a broken page layout wiping good data.
- **Polite scraping**: a configurable delay between requests, retries with exponential backoff and rotating browser User-Agents.
- **Scrape-only mode**: without database credentials, the scrapers still run and save JSON files to `data/current/`.
- **Weekly automation**: a GitHub Actions workflow runs every Thursday and uploads the logs and scraped data as artifacts.
- **Discord notifications**: get a summary of each run (records and changes per scraper).
- **Read-only, secure API**: the API only allows `GET`, reads with the Supabase **anon key** so Row Level Security applies, and supports an optional `X-Api-Key` header.
- **Interactive docs**: Swagger UI at `/docs`, generated automatically by FastAPI.
- **Integration tests**: 53 tests that call every endpoint against the real database.

## 🧰 Tech stack

| Area                   | Tools                                   |
| ---------------------- | --------------------------------------- |
| Scraping               | `requests`, `beautifulsoup4`, `lxml`    |
| Database               | Supabase (PostgreSQL) via `supabase-py` |
| API                    | `fastapi`, `uvicorn`, `pydantic`        |
| Config and logging     | `python-dotenv`, `loguru`               |
| Testing                | `pytest`, `pytest-cov`, `httpx`         |
| Automation and hosting | GitHub Actions, Render                  |

## 📁 Project structure

```
ewu-server-v3/
├── main.py                  # Entry point: runs every scraper and syncs to the DB
├── api/
│   ├── main.py              # FastAPI app, CORS, /api/health, /api/last-update
│   ├── dependencies.py      # Supabase anon client + X-Api-Key check
│   └── routes/              # One router per topic
│       ├── academic.py      # departments, programs, grade scale, deadlines, calendar
│       ├── people.py        # faculty, governance, alumni
│       ├── campus.py        # clubs, events, notices, helpdesk, proctor schedule
│       ├── finance.py       # tuition fees, scholarships
│       ├── info.py          # documents, policies, newsletters, partnerships
│       ├── courses.py       # course programs and course offerings
│       └── search.py        # cross-table search
├── scrapers/
│   ├── base_scraper.py      # BaseScraper: fetch → parse → validate → save
│   └── ewu/                 # One scraper per EWU page / data type
├── database/
│   ├── schema.sql           # All tables, indexes, triggers and RLS policies
│   ├── db_manager.py        # Supabase wrapper (service-role key, used by scrapers)
│   └── migrate.py           # One-time loader for manually collected JSON data
├── config/settings.py       # Every setting, read from environment variables
├── utils/
│   ├── diff_checker.py      # Compares old vs. new records (added/modified/removed)
│   ├── notifier.py          # Discord webhook notifications
│   ├── logger.py            # loguru setup (console + rotating log files)
│   └── validators.py        # Required-field validation helpers
├── tests/                   # API integration tests (pytest)
├── docs/source_mapping.json # Which EWU URL each dataset comes from
├── .github/workflows/weekly_update.yml  # Weekly scrape job
├── render.yaml / Procfile   # Deployment config for the API
└── requirements.txt
```

## 🚀 Getting started

### Prerequisites

- **Python 3.11** (the version used in CI and on Render)
- A free **[Supabase](https://supabase.com/)** project (optional for scrape-only mode)

### 1. Clone and install

```bash
git clone https://github.com/SamirHossain2001/ewu-server-v3.git
cd ewu-server-v3

python -m venv venv
# macOS / Linux
source venv/bin/activate
# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Create the database

In your Supabase dashboard, open **SQL Editor**, paste the contents of [`database/schema.sql`](database/schema.sql) and run it. This creates every table, index, `updated_at` trigger and read policy.

### 3. Configure environment variables

Create a `.env` file in the project root. It is ignored by git, so it never gets committed.

```env
# Supabase (Project Settings → API)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key   # used by scrapers (write access)
SUPABASE_ANON_KEY=your-anon-key                   # used by the API (read-only)

# Optional
DISCORD_WEBHOOK_URL=
API_SECRET_KEY=
ENV=development
```

## ⚙️ Configuration

All settings live in [`config/settings.py`](config/settings.py) and are read from environment variables (or `.env`).

| Variable                    | Default       | Used by           | Description                                                              |
| --------------------------- | ------------- | ----------------- | ------------------------------------------------------------------------ |
| `SUPABASE_URL`              | –             | Scrapers, API     | Your Supabase project URL.                                               |
| `SUPABASE_SERVICE_ROLE_KEY` | –             | Scrapers, migrate | Key with write access. **Keep it secret.**                               |
| `SUPABASE_ANON_KEY`         | –             | API, tests        | Public read-only key (Row Level Security applies). Required for the API. |
| `DISCORD_WEBHOOK_URL`       | _(empty)_     | Scrapers          | Where run summaries are posted. Skipped if empty.                        |
| `SCRAPE_DELAY_SECONDS`      | `3`           | Scrapers          | Pause between page requests.                                             |
| `MAX_RETRIES`               | `3`           | Scrapers          | Retry attempts per URL (exponential backoff).                            |
| `REQUEST_TIMEOUT`           | `30`          | Scrapers          | HTTP timeout in seconds.                                                 |
| `ENV`                       | `development` | API               | Set to `production` to **require** `API_SECRET_KEY`.                     |
| `API_SECRET_KEY`            | _(empty)_     | API               | If set, clients must send it as the `X-Api-Key` header.                  |
| `API_HOST`                  | `127.0.0.1`   | API               | Host when running `python api/main.py`.                                  |
| `API_PORT`                  | `8000`        | API               | Port when running `python api/main.py`.                                  |
| `API_ALLOWED_ORIGINS`       | `*`           | API               | Comma-separated list of CORS origins.                                    |

## 🛠️ Usage

### Run the scrapers

```bash
python main.py
```

Each scraper fetches its pages, saves a JSON snapshot to `data/current/<scraper>.json` and syncs the database. A summary table is printed at the end:

```
  <scraper name>                 | <status>             | records: <n> | changes: <n> | <seconds>s
```

Possible statuses: `success`, `no_data`, `skipped_high_change`, `upsert_failed` and `error: ...`.

- **First run on an empty or very different database?** Use `--force` to bypass the 30% safety threshold:

  ```bash
  python main.py --force
  ```

- **No Supabase credentials?** The pipeline logs a warning and runs in **scrape-only mode**: data is still saved to `data/current/`, but nothing is written to the database.

### Run the API locally

```bash
uvicorn api.main:app --reload
```

Then open **http://127.0.0.1:8000/docs** for the interactive Swagger UI.

### Call the API

```bash
# Health check (no key needed)
curl http://127.0.0.1:8000/api/health

# List undergraduate tuition fees
curl "http://127.0.0.1:8000/api/tuition-fees?level=undergraduate"

# If API_SECRET_KEY is set, include the header
curl -H "X-Api-Key: YOUR_KEY" "https://ewu-server.onrender.com/api/search?q=computer"
```

### Load manually collected data (optional)

Some tables (departments, programs, grade scale, alumni, proctor schedule, partnerships, policies and course catalogs) are not covered by the scrapers. They are filled once from JSON files by [`database/migrate.py`](database/migrate.py):

```bash
python -m database.migrate           # upsert everything
python -m database.migrate --clean   # wipe the target tables first, then load
```

The script reads from a `manually_scrapped_data/` folder in the project root, including the `courses_undergraduate/` and `courses_graduate/` subfolders. **This folder is not included in the repository**, so you need to supply it yourself. The expected file names are listed in `FILE_TABLE_MAP` inside `migrate.py`.

## 📚 API reference

- **Base URL (live):** `https://ewu-server.onrender.com`
- **All endpoints are `GET`.** Every route except `/api/health` and `/api/last-update` checks the `X-Api-Key` header when `API_SECRET_KEY` is set.

**Response format**

```json
{ "data": [ ... ], "count": 42 }
```

Single-item endpoints return `{ "data": { ... } }`. Errors: `401` for an invalid or missing API key, `404` when an item is not found.

<details open>
<summary><b>Meta</b></summary>

| Endpoint           | Description                                         |
| ------------------ | --------------------------------------------------- |
| `/api/health`      | Returns `{"status": "healthy"}`.                    |
| `/api/last-update` | The most recent scraper run from `scrape_metadata`. |

</details>

<details>
<summary><b>Academic</b></summary>

| Endpoint                     | Query parameters                                                                     | Description                                       |
| ---------------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------- |
| `/api/departments`           | `faculty`                                                                            | All departments; partial-match filter by faculty. |
| `/api/programs`              | `degree_type`, `department_id`, `limit` (1–200, default 50), `offset`                | Degree programs with their department.            |
| `/api/programs/{program_id}` | –                                                                                    | One program by ID.                                |
| `/api/grade-scale`           | –                                                                                    | Letter grades and grade points.                   |
| `/api/admission-deadlines`   | `level`, `semester`                                                                  | Application deadlines and admission test dates.   |
| `/api/academic-calendar`     | `semester`, `program_type`, `calendar_type` (`academic_calendar` or `exam_schedule`) | Calendar events, sorted by date.                  |

</details>

<details>
<summary><b>People</b></summary>

| Endpoint                    | Query parameters                                               | Description                                 |
| --------------------------- | -------------------------------------------------------------- | ------------------------------------------- |
| `/api/faculty`              | `department_id`, `name`, `limit` (1–200, default 50), `offset` | Faculty members; partial-match name search. |
| `/api/faculty/{faculty_id}` | –                                                              | One faculty member by ID.                   |
| `/api/governance`           | `body` (`academic_council`, `board_of_trustees`, `syndicate`)  | Members of university governing bodies.     |
| `/api/alumni`               | –                                                              | Notable alumni.                             |

</details>

<details>
<summary><b>Campus</b></summary>

| Endpoint                | Query parameters            | Description                       |
| ----------------------- | --------------------------- | --------------------------------- |
| `/api/clubs`            | –                           | Student clubs.                    |
| `/api/events`           | –                           | Events, newest first.             |
| `/api/notices`          | `limit` (1–500, default 50) | Notice-board posts, newest first. |
| `/api/helpdesk`         | `category`                  | Helpdesk contact emails.          |
| `/api/proctor-schedule` | –                           | Proctor office schedule.          |

</details>

<details>
<summary><b>Finance</b></summary>

| Endpoint            | Query parameters | Description                                       |
| ------------------- | ---------------- | ------------------------------------------------- |
| `/api/tuition-fees` | `level`          | Per-credit fees, totals and admission fees (BDT). |
| `/api/scholarships` | –                | Scholarships and financial aid.                   |

</details>

<details>
<summary><b>Information</b></summary>

| Endpoint                | Description                                                                                                                                                                                                                                  |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/api/documents`        | List of university documents (`slug`, `title`, `source_file`).                                                                                                                                                                               |
| `/api/documents/{slug}` | Full document content. Slugs: `grading`, `policies`, `rules`, `payment-procedure`, `career-counseling`, `admission-process`, `admission-requirements`, `sexual-harassment-policy`, `facilities`. Other slugs may exist from the data loader. |
| `/api/policies`         | University policies.                                                                                                                                                                                                                         |
| `/api/newsletters`      | Newsletters, newest year first.                                                                                                                                                                                                              |
| `/api/partnerships`     | Partner institutions.                                                                                                                                                                                                                        |

</details>

<details>
<summary><b>Courses</b></summary>

| Endpoint                               | Query parameters                                                                              | Description                                                        |
| -------------------------------------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| `/api/courses/programs`                | `level` (`undergraduate`/`graduate`), `search`                                                | Program summaries (code, name, credits, department).               |
| `/api/courses/programs/{program_code}` | –                                                                                             | Full program, with its courses grouped by section.                 |
| `/api/courses`                         | `level`, `program`, `course_type`, `section`, `search`, `limit` (1–500, default 50), `offset` | Course offerings; `search` matches title or code.                  |
| `/api/courses/{course_code}`           | `program`                                                                                     | One course. Returns a list if the code exists in several programs. |

</details>

<details>
<summary><b>Search</b></summary>

| Endpoint      | Query parameters | Description                                                                                                                     |
| ------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `/api/search` | `q` (required)   | Partial-match search across programs, faculty, clubs, events and policies (up to 10 results each). Results are grouped by type. |

</details>

## 🔍 How the scraper pipeline works

Every scraper extends `BaseScraper` ([`scrapers/base_scraper.py`](scrapers/base_scraper.py)) and follows the same lifecycle:

```
get_urls()  →  fetch() with retries  →  parse() into dicts  →  validate()  →  save() to data/current/
```

`main.py` then syncs each result to its table in one of three modes (set in `SCRAPER_CONFIG`):

| Mode                      | How it works                                                                                                                                                     | Used by                                          |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| **Diff upsert** (default) | Compares the new data with the database using a key field. Upserts only if something changed, and **skips** the update if more than 30% of records would change. | Most scrapers                                    |
| **`replace_all`**         | Deletes every row, then inserts the fresh data.                                                                                                                  | Academic calendar, admission deadlines           |
| **`shared_table`**        | Several scrapers write one row each (by `slug`) to the same table. No threshold check.                                                                           | The 9 document scrapers → `university_documents` |

After each scraper, the run is logged to `scrape_metadata`, and a summary is sent to Discord at the end.

<details>
<summary><b>All scrapers and their sources</b></summary>

| Scraper                        | Table                  | Source (on `ewubd.edu` unless noted)                                 |
| ------------------------------ | ---------------------- | -------------------------------------------------------------------- |
| `TuitionFeesScraper`           | `tuition_fees`         | `/undergraduate-tuition-fees`, `/graduate-programs-tuition-fees`     |
| `ScholarshipsScraper`          | `scholarships`         | `/scholarships-financial-aid`                                        |
| `NoticesScraper`               | `notices`              | `/notice-board` (paginated, up to 30 pages)                          |
| `EventsScraper`                | `events`               | `/events`                                                            |
| `ClubsScraper`                 | `clubs`                | `/clubs`                                                             |
| `FacultyScraper`               | `faculty_members`      | `/search-faculty` (tries JSON endpoints first, then parses the page) |
| `NewslettersScraper`           | `newsletters`          | `/newsletters`                                                       |
| `AdmissionDeadlinesScraper`    | `admission_deadlines`  | `/undergraduate-dates-deadline`, `/graduate-dates-deadline`          |
| `HelpdeskScraper`              | `helpdesk_contacts`    | `/notice-details/online-helpdesk-list-email-accounts`                |
| `GovernanceScraper`            | `governance_members`   | `/board-trustees`, `/syndicate`, `/academic-council`                 |
| `AcademicCalendarScraper`      | `academic_calendar`    | `/academic-calendar` (latest year's tab and its detail pages)        |
| `GradingScraper`               | `university_documents` | `/grades-rules-and-regulations`                                      |
| `PoliciesDocScraper`           | `university_documents` | `/ewu-policies`                                                      |
| `RulesScraper`                 | `university_documents` | `/student-rules-regulation`                                          |
| `PaymentScraper`               | `university_documents` | `/payment-procedure`                                                 |
| `CareerCenterScraper`          | `university_documents` | `/career-counseling-center`                                          |
| `AdmissionProcessScraper`      | `university_documents` | `admission.ewubd.edu`                                                |
| `AdmissionRequirementsScraper` | `university_documents` | `admission.ewubd.edu`                                                |
| `SexualHarassmentScraper`      | `university_documents` | `/ewu-sexual-harassment-elimination-and-prevention-policy`           |
| `FacilitiesScraper`            | `university_documents` | `/research-facilities`, `/campus-life`                               |
| `AboutScraper`                 | _(JSON file only)_     | `/history`, `/vision-mission-ewu`                                    |

</details>

## 🗄️ Database

The full schema is in [`database/schema.sql`](database/schema.sql). Every table has a UUID `id` and `created_at`; most also have an `updated_at` column that a trigger keeps current.

| Table                                                                                                                                                                                                         | Contents                                                 | Filled by                                |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- | ---------------------------------------- |
| `tuition_fees`, `scholarships`, `notices`, `events`, `clubs`, `faculty_members`, `newsletters`, `admission_deadlines`, `helpdesk_contacts`, `governance_members`, `academic_calendar`, `university_documents` | Live university data                                     | Scrapers (weekly), plus the initial load |
| `departments`, `programs`, `grade_scale`, `notable_alumni`, `proctor_schedule`, `partnerships`, `policies`                                                                                                    | Mostly static reference data                             | `database/migrate.py`                    |
| `course_programs`, `course_offerings`                                                                                                                                                                         | Program curricula and course details                     | `database/migrate.py`                    |
| `scrape_metadata`                                                                                                                                                                                             | One row per scraper run (status, record count, duration) | Scrapers                                 |

**Security:** Row Level Security is enabled on all tables. A `public_read` policy lets the **anon** role `SELECT` from the data tables. `scrape_metadata` has no anon read policy, so it stays internal.

## ⏱️ Automation and deployment

### Weekly scrape (GitHub Actions)

[`.github/workflows/weekly_update.yml`](.github/workflows/weekly_update.yml) runs **every Thursday at 04:00 Bangladesh time** (`0 22 * * 3` UTC). You can also trigger it manually from the **Actions** tab. The workflow:

1. Installs Python 3.11 and the requirements.
2. Builds a `.env` from repository secrets.
3. Runs `python main.py`.
4. Uploads `logs/` (kept 30 days) and `data/current/` (kept 7 days) as artifacts.
5. Sends a success or failure message to Discord.

Add these under **Settings → Secrets and variables → Actions**:
`SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_ANON_KEY`, `DISCORD_WEBHOOK_URL`.

### API hosting (Render)

The API is deployed as a Render web service using [`render.yaml`](render.yaml):

```bash
# build
pip install -r requirements.txt
# start
uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

`render.yaml` sets `ENV=production`, which means **`API_SECRET_KEY` must be set**, or the protected endpoints return `500`. Also add `SUPABASE_URL` and `SUPABASE_ANON_KEY` in the Render dashboard. A [`Procfile`](Procfile) with the same start command is included for Heroku-style hosts.

## 🧪 Testing

```bash
pytest
# with coverage
pytest --cov=api
```

These are **integration tests**. They call every endpoint through FastAPI's `TestClient` against your **real Supabase database**, without mocks. The whole suite is skipped automatically if `SUPABASE_ANON_KEY` is not set or the database cannot be reached. The tests cover meta, academic, people, finance, information, campus, courses, search and API-key authentication.

## ➕ Adding a new scraper

1. Create `scrapers/ewu/my_data.py` with a class that extends `BaseScraper`. Set a `name` and implement `get_urls()` and `parse(html, url)`, which returns a list of dicts.
2. Export it in [`scrapers/ewu/__init__.py`](scrapers/ewu/__init__.py).
3. Add a table for it to `database/schema.sql` (and apply it in Supabase). Remember to add the table to the RLS and `public_read` loops.
4. Register it in `SCRAPER_CONFIG` in [`main.py`](main.py) with its `table`, `key_field` and `on_conflict` columns.
5. _(Optional)_ Add a route in `api/routes/` to expose the data.

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository and create a branch: `git checkout -b feature/my-change`
2. Make your changes and run `pytest`.
3. Open a pull request describing what you changed and why.

Found a scraper returning bad data? Please [open an issue](https://github.com/SamirHossain2001/ewu-server-v3/issues) and include the page URL.

## 📄 License

Released under the [MIT License](LICENSE).

> This project was developed as part of a capstone project at East West University. It is not an official university service, and all scraped content belongs to its original owners.
