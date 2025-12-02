import requests
import pandas as pd

# --- API Request ---
# extracting everything
url = "https://api.stackexchange.com/2.3/questions?order=desc&sort=activity&site=stackoverflow"

# extracting what contains python:
#url = "https://api.stackexchange.com/2.3/questions?order=desc&sort=activity&tagged=python&site=stackoverflow"

response = requests.get(url)
data = response.json()

# --- Parse the response ---
posts = []
for item in data.get('items', []):
    title = item.get('title', 'No title')
    author = item.get('owner', {}).get('display_name', 'Anonymous')
    score = item.get('score', 0)
    link = item.get('link', '')
    posts.append([title, author, score, link])

# --- Save to CSV ---
df = pd.DataFrame(posts, columns=['Title', 'Author', 'Score', 'URL'])
df.to_csv('data/stack_questions.csv', index=False, encoding='utf-8')

print("Data saved to data/stack_questions.csv")
