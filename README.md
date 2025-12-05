#  StackOverflow Scraper & Data Visualization

This project collects, analyzes, and visualizes StackOverflow questions based on a user-defined keyword.
It was inspired by the *“Scraping Reddit Using Python”* tutorial on GeeksForGeeks, but since Reddit API access was not approved, this project uses the **StackExchange API** instead.

The pipeline consists of:

1. **Scraping StackOverflow search results** using a keyword
2. **Saving results into a structured CSV file**
3. **Performing sentiment, score, and text-length analysis**
4. **Generating interactive charts and visualizations**
5. **Allowing users to click chart items to open the original StackOverflow question**

---

##  Features

###  Web Scraping

The scraper collects StackOverflow questions whose titles contain a chosen keyword. Each scraped entry includes:

* Question title
* Author name
* Score
* Direct URL

✔ Uses the official **StackExchange API**
✔ Saves data into: `data/stack_questions.csv`

 Source file: `keywordstack_scraper.py`

---

##  Data Analysis & Visualization

Once the CSV is populated, the analysis script loads the data and creates:

### 1. Top 5 Questions by Score

Interactive horizontal bar chart — clicking a bar opens the question.

### 2. Top 5 Longest Question Titles

Shows the most verbose/complex titles.

### 3. Word Cloud

Highlights the most frequent words in all question titles.

### 4. Author Activity Pie Chart

Shows which authors appear most often in your dataset.

### 5. Score Ranking (All Rows)

Full interactive score ranking chart.

### 6. Sentiment Ranking (All Rows)

Sentiment polarity extracted using TextBlob.

### 7. Title Length vs Score Scatter Plot

### 8. Sentiment vs Title Length Scatter Plot

 Source file: `analyse_stack_plus.py`

All interactive plots are built using **Plotly**, with click handlers enabled.

---

##  Project Structure

```
/project-root
│
├── data/
│   └── stack_questions.csv        # Auto-generated scraped data
│
├── keywordstack_scraper.py        # Scrapes StackOverflow by keyword
├── analyse_stack_plus.py          # Analysis and visualizations
├── README.md                      # Project documentation
└── requirements.txt               # Python dependencies
```

---

##  Installation

Make sure you have Python 3.8+ installed.

Install dependencies:

```bash
pip install -r requirements.txt
```

### Required Packages

* requests
* pandas
* textblob
* matplotlib
* numpy
* plotly
* wordcloud


##  Usage

### *. Run the scraper

```bash
python keywordstack_scraper.py
```

You will be prompted for a keyword:

```
Enter a keyword to scrape from StackOverflow: python
```

This generates:

```
data/stack_questions.csv
```

---

### 2. Run the analysis

```bash
python analyse_stack_plus.py
```

All charts will open in your default browser.

✔ Hover over bars → see details
✔ Fully interactive charts

---

##  Example Use Cases

* Discover most upvvoted questions for a topic
* Analyze sentiment across developer questions
* Explore relationships between title length and score
* Generate word clouds for learning patterns
* Identify highly active StackOverflow contributors

---


##  Inspiration

This project was inspired by the tutorial:
**"Scraping Reddit using Python" (GeeksForGeeks)**
but adapted to StackOverflow due to Reddit API limitations.

---
