# StackOverflow Insights Dashboard

A modern, interactive web application that **scrapes, stores, analyzes, and visualizes StackOverflow questions in real time** — directly from your browser.

This project began as a **simple keyword-based scraper with offline analytics**, and has evolved into a **full end-to-end data pipeline and interactive dashboard** with persistent storage, live scraping, advanced metrics, and rich visualizations.

---

## 🚀 What This App Does

* Scrapes StackOverflow questions **live** using the official StackExchange API
* Persists results in a **SQLite database** (not just CSVs)
* Enriches data with:

  * Sentiment analysis
  * Title length metrics
  * A custom **Hotness score**
* Visualizes insights using **interactive Bokeh charts**
* Provides a **Flask-based web dashboard** with:

  * Keyword comparison
  * Click-to-open StackOverflow links
  * Loading states & animations
  * Data reset functionality

---

## 📜 Evolution of the Application

### 🕰️ Old Version — Legacy Scripts

The original version consisted of standalone, script-based workflows.

#### 1. `keywordstack_scraper.py`

* Scraped StackOverflow questions by keyword
* Stored results in a single CSV file: `data/stack_questions.csv`
* One keyword per run

#### 2. `analyse_stack_plus.py` / `analyse_stack_plus_v2.py`

* Loaded CSV data
* Performed basic analysis:

  * Scores
  * Title length
  * Sentiment (TextBlob)
* Generated static or standalone interactive HTML reports (Plotly / Bokeh)
* Allowed clicking charts to open StackOverflow links

#### ❌ Limitations of the Old App

* No persistent storage (CSV overwritten on each run)
* No keyword comparison
* No web interface
* Tight coupling between scraping, analysis, and visualization
* Hard to extend, reuse, or deploy

---

### 🚀 Current Version — Interactive Web Application

The project is now a **fully integrated analytics dashboard** following a clean pipeline:

> **Scrape → Store → Process → Score → Visualize → Explore**

#### Key Upgrades

* Live scraping triggered directly from the **web UI**
* **SQLite database** as the primary data store: `data/stack_questions.db`
* Rich feature engineering:

```
Hotness = Score + 2 × AnswerCount + (ViewCount / 100)
```

* Keyword comparison mode (e.g. `python` vs `javascript`)
* Fully interactive **Bokeh** visualizations
* Polished UX: loading overlays, animations, click actions
* One-click **Reset All Data** functionality

---

## 🧠 How It Works — Data Pipeline

```text
[ User enters keyword in Web UI ]
            ↓
[ Flask backend receives POST request ]
            ↓
[ StackExchange API queried ]
            ↓
[ Data upserted into SQLite database ]
            ↓
[ Data cleaning & enrichment ]
            ↓
[ Hotness + sentiment + time features ]
            ↓
[ Bokeh charts generated ]
            ↓
[ Flask renders dashboard.html ]
            ↓
[ Browser: interactive charts & links ]
```

---

## 📂 Project Structure

```
python_scraper_project/
│
├── app.py                        # Flask dashboard entry point
│
├── stack_scraper.py              # Main scraper (API → SQLite)
├── keywordstack_scraper.py       # Legacy CSV-based scraper
├── analyse_stack_plus.py         # Legacy Plotly analysis script
├── analyse_stack_plus_v2.py      # Legacy standalone Bokeh report
│
├── data/
│   ├── stack_questions.db        # Primary SQLite database
│   └── stack_questions.csv       # Optional CSV export
│
├── templates/
│   └── dashboard.html            # Bokeh-powered dashboard UI
│
├── Dockerfile                    # Container image definition
├── docker-compose.yml            # Docker orchestration
│
└── README.md
```

> **Note:** A future refactor will move logic into a `src/stackviz/` package with clear module boundaries.

---

## ⚙️ Installation — Local (Without Docker)

### 1️⃣ Create a virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Ensure data directory exists

```bash
mkdir -p data
```

### 4️⃣ Run the Flask app

```bash
python app.py
```

Open your browser at:

```
http://localhost:5000
```

---

## 🐳 Running with Docker & Docker Compose

The application can be run fully containerized.

### 1️⃣ Build & run

```bash
docker-compose up --build
```

This will:

* Build the Docker image using `Dockerfile`
* Start the Flask app inside a container
* Expose the web UI on the port defined in `docker-compose.yml` (usually 5000)

Open:

```
http://localhost:5000
```

### 2️⃣ Stop containers

```bash
docker-compose down
```

> **Note:** The `data/` directory is typically mounted as a volume, so the SQLite database persists across restarts.

---

## 🖥️ Usage

### From the Web Dashboard

1. Open the app in your browser
2. Enter a keyword (e.g. `python`)
3. Optionally enter a comparison keyword (e.g. `javascript`)
4. Click **Load Data**
5. Explore the interactive charts

#### Interactions

* Click bars or points → open the StackOverflow question
* Hover for metadata (sentiment, views, score, hotness)
* Use **Reset All Data** to clear the database

---

### Legacy CLI Workflows (Optional)

#### 1. CSV-only scraper

```bash
python keywordstack_scraper.py
```

Creates:

```
data/stack_questions.csv
```

#### 2. Standalone analysis report

```bash
python analyse_stack_plus_v2.py
```

Generates a self-contained HTML report with interactive Bokeh charts.

> These scripts remain for experimentation and backward compatibility. The Flask dashboard is the recommended workflow.

---

## 📊 Insights & Visualizations

The dashboard currently includes:

* 🔥 Top 5 Hottest Questions
* 📏 Top 5 Longest Titles
* 👤 Top Authors
* 🔥 Hotness Ranking (Top N)
* 😊 Sentiment vs Hotness
* 📏 Title Length vs Hotness
* 📅 Questions Over Time
* 🏷️ Top Tags
* ☁️ Word Cloud of Titles

All relevant charts support **click-to-open StackOverflow links**.

---

## 🧰 Tech Stack

* Python 3.10+
* Flask — web framework
* Bokeh — interactive visualization
* SQLite — persistent storage
* Pandas — data processing
* Requests — StackExchange API client
* TextBlob — sentiment analysis
* Matplotlib + WordCloud — word cloud generation
* Docker & docker-compose — containerized deployment

---

## 🌱 Roadmap

* Refactor into `src/stackviz/` package
* Add REST API endpoints
* Advanced filtering & pagination
* User-configurable Hotness weights
* Unit & integration tests
* Production-grade Docker setup
* Cloud deployment (Render, Fly.io, etc.)

---

## 🙏 Inspiration

Originally inspired by:

> **“Scraping Reddit using Python” — GeeksForGeeks**

Due to Reddit API restrictions, the project was rebuilt on top of the **StackExchange API** and expanded into a full analytics dashboard.

---

## 🎉 Final Notes

What started as a CSV-based scraping exercise is now a **live, interactive StackOverflow analytics platform**.

You can scrape, persist, analyze, and explore developer questions end-to-end — locally or fully containerized with Docker.

If you want to push this toward a **production-grade, modular data product**, that’s the natural next step.
