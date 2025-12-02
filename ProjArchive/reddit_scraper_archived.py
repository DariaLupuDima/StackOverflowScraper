import praw
import csv

# --- Connect to Reddit API ---
reddit = praw.Reddit(
    client_id='XyS1zKxXsJp0Wu',               # Replace with your own when possible
    client_secret='JmK4cO0PNN_U7dO9XiKah3Ssc', # Replace with your own when possible
    user_agent='reddit_scraper:v1.0 (by u/Daria2_grayCats)'
)

# --- Choose Subreddit ---
subreddit_name = 'learnpython'
subreddit = reddit.subreddit(subreddit_name)

# --- Define output file ---
output_path = 'data/reddit_posts.csv'

# --- Open CSV file to save data ---
with open(output_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Title', 'Author', 'Score', 'URL'])

    # --- Loop through hot posts ---
    for post in subreddit.hot(limit=50):  # Changed to 50 for better dataset
        title = post.title
        author = str(post.author)
        score = post.score
        url = post.url
        writer.writerow([title, author, score, url])

print(f"Data has been saved to {output_path}")
