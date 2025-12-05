import pandas as pd       # Load and process dataset
import html               # Decode HTML symbols
from textblob import TextBlob  # Sentiment analysis
from wordcloud import WordCloud # Word cloud generation
import matplotlib.pyplot as plt # Word cloud plotting
import numpy as np        # Numeric arrays for metadata
import plotly.express as px # Interactive charts
import plotly.graph_objects as go
import plotly.io as pio    # Plot rendering control



# Plotly style settings
pio.renderers.default = "browser"
pio.templates.default = "plotly_white"
pio.defaults.hoverlabel = dict(bgcolor="white", font_size=14, namelength=-1)

# Load and clean CSV data
df = pd.read_csv('data/stack_questions.csv') #load data
df = df[df['Title'].notna()]
df['Title'] = df['Title'].apply(html.unescape) #decode html symbols
df['Title Length'] = df['Title'].apply(len)
df['Short Title'] = df['Title'].apply(lambda x: x if len(x) <= 80 else x[:77] + "...")
df['Sentiment'] = df['Title'].apply(lambda x: TextBlob(x).sentiment.polarity)

# Custom metadata for hover + click
customdata_all = np.stack([df['Title'], df['Author'], df['URL']], axis=-1)

# ============================================================
#  PLOT 1 — Top 5 Questions by Score
# ============================================================
top_score = df.sort_values(by='Score', ascending=False).head(5)
customdata_score = np.stack([top_score['Title'], top_score['Author'], top_score['URL']], axis=-1)

fig1 = px.bar(
    top_score,
    x='Score',
    y='Short Title',
    orientation='h',
    title='Top 5 Highest-Scoring StackOverflow Questions',
    color='Score',
    color_continuous_scale='Blues'
)

fig1.update_traces(
    customdata=customdata_score,
    hovertemplate=
        "<b>Title:</b> %{customdata[0]}<br>"
        "<b>Author:</b> %{customdata[1]}<br>"
        "<b>Link:</b> %{customdata[2]}<br>"
        "<extra></extra>"
)
fig1.show()

# ============================================================
#  PLOT 2 — Top 5 Longest Titles
# ============================================================
top_length = df.sort_values(by='Title Length', ascending=False).head(5)
customdata_length = np.stack([top_length['Title'], top_length['Author'], top_length['URL']], axis=-1)

fig2 = px.bar(
    top_length,
    x='Title Length',
    y='Short Title',
    orientation='h',
    title='Top 5 Longest StackOverflow Question Titles',
    color='Title Length',
    color_continuous_scale='Oranges'
)

fig2.update_traces(
    customdata=customdata_length,
    hovertemplate=
        "<b>Title:</b> %{customdata[0]}<br>"
        "<b>Author:</b> %{customdata[1]}<br>"
        "<b>Link:</b> %{customdata[2]}<br>"
        "<extra></extra>"
)
fig2.show()

# ============================================================
# PLOT 3 — Author Activity Pie Chart
# ============================================================
top_authors = df['Author'].value_counts().head(5).reset_index()
top_authors.columns = ['Author', 'Count']

fig4 = px.pie(
    top_authors,
    names='Author',
    values='Count',
    title='Top 5 Most Active Authors'
)

fig4.update_traces(
    hovertemplate=
        "<b>Author:</b> %{label}<br>"
        "<b>Posts:</b> %{value}<br>"
        "<extra></extra>"
)
fig4.show()

# ============================================================
#  PLOT 4 — Score Ranking (ALL rows) 
# ============================================================
fig5 = px.bar(
    df,
    x='Score',
    y='Short Title',
    orientation='h',
    title="Score Ranking of StackOverflow Questions",
    color='Score',
    color_continuous_scale='Purples'
)

fig5.update_traces(
    customdata=customdata_all,
    hovertemplate=
        "<b>Title:</b> %{customdata[0]}<br>"
        "<b>Author:</b> %{customdata[1]}<br>"
        "<b>Link:</b> %{customdata[2]}<br>"
        "<extra></extra>"
)
fig5.show()

# ============================================================
# PLOT 5 — Sentiment Ranking (ALL rows) 
# ============================================================
fig6 = px.bar(
    df,
    x='Sentiment',
    y='Short Title',
    orientation='h',
    title="Sentiment Ranking of Question Titles",
    color='Sentiment',
    color_continuous_scale='RdYlGn'
)

fig6.update_traces(
    customdata=customdata_all,
    hovertemplate=
        "<b>Sentiment:</b> %{x}<br>"
        "<b>Title:</b> %{customdata[0]}<br>"
        "<b>Author:</b> %{customdata[1]}<br>"
        "<b>Link:</b> %{customdata[2]}<br>"
        "<extra></extra>"
)
fig6.show()

# ============================================================
#  PLOT 6 — Title Length vs Score
# ============================================================
fig7 = px.scatter(
    df,
    x='Title Length',
    y='Score',
    color='Score',
    color_continuous_scale='Teal',
    title="Title Length vs Score"
)

fig7.update_traces(
    customdata=customdata_all,
    hovertemplate=
        "<b>Title:</b> %{customdata[0]}<br>"
        "<b>Author:</b> %{customdata[1]}<br>"
        "<b>Score:</b> %{y}<br>"
        "<b>Link:</b> %{customdata[2]}<br>"
        "<extra></extra>"
)
fig7.show()

# ============================================================
#  PLOT 7 — Sentiment vs Title Length
# ============================================================
fig8 = px.scatter(
    df,
    x='Sentiment',
    y='Title Length',
    color='Sentiment',
    color_continuous_scale='RdYlGn',
    title="Sentiment vs Title Length"
)

fig8.update_traces(
    customdata=customdata_all,
    hovertemplate=
        "<b>Title:</b> %{customdata[0]}<br>"
        "<b>Author:</b> %{customdata[1]}<br>"
        "<b>Sentiment:</b> %{x}<br>"
        "<b>Link:</b> %{customdata[2]}<br>"
        "<extra></extra>"
)
fig8.show()

# ============================================================
#  PLOT 8 — Word Cloud 
# ============================================================
text = " ".join(df['Title'].tolist())
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

plt.figure(figsize=(12,6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title("Most Frequent Words in Question Titles")
plt.tight_layout()
plt.show()
