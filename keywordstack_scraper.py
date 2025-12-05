import requests      # Sends HTTP requests to the StackExchange API
import pandas as pd  # Stores, structures, and exports the scraped data

# Ask the user for a keyword to filter StackOverflow questions.
# This makes the scraper dynamic and allows targeted searches.
keyword = input("Enter a keyword to scrape from StackOverflow: ")

# Build the API request URL using the given keyword.
# The API will return questions sorted by votes that contain the keyword in the title.
url = (
    "https://api.stackexchange.com/2.3/search?"
    f"order=desc&sort=votes&intitle={keyword}&site=stackoverflow&pagesize=100"
)

# Send the GET request to StackOverflow and convert the response to a Python dictionary.
response = requests.get(url)
data = response.json()

# Extract relevant fields from each returned question.
# We only keep: Title, Author name, Score, and the URL of the question.
posts = []
for item in data.get('items', []):
    title = item.get('title', 'No title')
    author = item.get('owner', {}).get('display_name', 'Anonymous')
    score = item.get('score', 0)
    link = item.get('link', '')

    posts.append([title, author, score, link])

# Convert list into a DataFrame and export it as a CSV file.
# This file will later be used for data analysis and visualizations.
df = pd.DataFrame(posts, columns=['Title', 'Author', 'Score', 'URL'])
df.to_csv('data/stack_questions.csv', index=False, encoding='utf-8')

# Inform the user that the scraping process is done.
print(f" Scraped {len(df)} questions containing '{keyword}' and saved to data/stack_questions.csv")
