import requests
import pandas as pd

# --- Ask for keyword BEFORE scraping ---
keyword = input("Enter a keyword to scrape from StackOverflow: ")

# --- API request with keyword in title ---
url = (
    "https://api.stackexchange.com/2.3/search?"
    f"order=desc&sort=votes&intitle={keyword}&site=stackoverflow&pagesize=100"
)

response = requests.get(url)
data = response.json()

posts = []
for item in data.get('items', []):
    title = item.get('title', 'No title')
    author = item.get('owner', {}).get('display_name', 'Anonymous')
    score = item.get('score', 0)
    link = item.get('link', '')

    posts.append([title, author, score, link])

# Save to CSV
df = pd.DataFrame(posts, columns=['Title', 'Author', 'Score', 'URL'])
df.to_csv('data/stack_questions.csv', index=False, encoding='utf-8')

print(f" Scraped {len(df)} questions containing '{keyword}' and saved to data/stack_questions.csv")
