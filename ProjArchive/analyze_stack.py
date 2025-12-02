import pandas as pd
import html
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- Load and clean the dataset ---
df = pd.read_csv('data/stack_questions.csv')
df = df[df['Title'].notna()]
df['Title'] = df['Title'].apply(html.unescape)
df['Title Length'] = df['Title'].apply(len)
df['Short Title'] = df['Title'].apply(lambda x: x if len(x) <= 80 else x[:77] + '...')
df['Sentiment'] = df['Title'].apply(lambda x: TextBlob(x).sentiment.polarity)

# --- USER INPUT ---
keyword = input("Enter a keyword to search for in question titles: ")

# --- FILTERING ---
filtered = df[df['Title'].str.contains(keyword, case=False, na=False)]
top_score = df.sort_values(by='Score', ascending=False).head(5)
top_filtered = filtered.sort_values(by='Score', ascending=False).head(5)
top_length = df.sort_values(by='Title Length', ascending=False).head(5)

top_authors = df['Author'].value_counts().head(5).reset_index()
top_authors.columns = ['Author', 'Count']


# ============================================================
# 📊 PLOT 1 — Top 5 Questions by Score
# ============================================================

fig1 = px.bar(
    top_score,
    x='Score',
    y='Short Title',
    orientation='h',
    title='Top 5 StackOverflow Questions by Score',
    hover_data=['Title', 'Author', 'Score', 'URL'],
    color='Score',
    color_continuous_scale='Blues'
)

fig1.update_layout(yaxis={'categoryorder': 'total ascending'})
fig1.show()


# ============================================================
# 📊 PLOT 2 — Keyword Matches
# ============================================================

if not top_filtered.empty:
    fig2 = px.bar(
        top_filtered,
        x='Score',
        y='Short Title',
        orientation='h',
        title=f"Top Questions Containing '{keyword}'",
        hover_data=['Title', 'Author', 'Score', 'URL'],
        color='Score',
        color_continuous_scale='Greens'
    )
    fig2.update_layout(yaxis={'categoryorder': 'total ascending'})
    fig2.show()


# ============================================================
# 📊 PLOT 3 — Longest Titles
# ============================================================

fig3 = px.bar(
    top_length,
    x='Title Length',
    y='Short Title',
    orientation='h',
    title='Top 5 Longest StackOverflow Question Titles',
    hover_data=['Title', 'Author', 'URL'],
    color='Title Length',
    color_continuous_scale='Oranges'
)

fig3.update_layout(yaxis={'categoryorder': 'total ascending'})
fig3.show()


# ============================================================
# ☁️ PLOT 4 — Word Cloud (static)
# ============================================================

text = ' '.join(df['Title'].tolist())
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

plt.figure(figsize=(12, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title("Most Frequent Words in Question Titles")
plt.tight_layout()
plt.show()


# ============================================================
# 🥧 PLOT 5 — Author Activity Pie Chart
# ============================================================

fig5 = px.pie(
    top_authors,
    names='Author',
    values='Count',
    title='Top 5 Most Active Authors',
    hover_data=['Count']
)

fig5.show()


# ============================================================
# 📊 PLOT 6 — FIXED Histogram with Real Hover (Score)
# ============================================================

hist_values, bin_edges = np.histogram(df['Score'], bins=20)

fig6 = go.Figure()

# Add static (non-hoverable) bars
for i in range(len(hist_values)):
    fig6.add_shape(
        type="rect",
        x0=bin_edges[i],
        x1=bin_edges[i+1],
        y0=0,
        y1=hist_values[i],
        line=dict(color="mediumpurple"),
        fillcolor="mediumpurple",
        opacity=0.5
    )

# Add invisible scatter for hover data
fig6.add_trace(go.Scatter(
    x=df['Score'],
    y=[0] * len(df),
    mode='markers',
    marker=dict(color='rgba(0,0,0,0)', size=12),
    hovertemplate=
        "<b>Exact Score:</b> %{x}<br>" +
        "<b>Title:</b> %{customdata[0]}<br>" +
        "<b>Author:</b> %{customdata[1]}<br>" +
        "<b>Link:</b> %{customdata[2]}<br><extra></extra>",
    customdata=df[['Title', 'Author', 'URL']]
))

fig6.update_layout(
    title="Distribution of Post Scores",
    xaxis_title="Score",
    yaxis_title="Count"
)

fig6.show()


# ============================================================
# 📊 PLOT 7 — Title Length vs Score
# ============================================================

fig7 = px.scatter(
    df,
    x='Title Length',
    y='Score',
    hover_data=['Title', 'Author', 'URL'],
    title='Title Length vs. Score',
    color='Score',
    color_continuous_scale='Teal'
)

fig7.show()


# ============================================================
# 📊 PLOT 8 — FIXED Sentiment Histogram with Real Hover
# ============================================================

hist_values, bin_edges = np.histogram(df['Sentiment'], bins=20)

fig8 = go.Figure()

# Add static bars
for i in range(len(hist_values)):
    fig8.add_shape(
        type="rect",
        x0=bin_edges[i],
        x1=bin_edges[i+1],
        y0=0,
        y1=hist_values[i],
        line=dict(color="salmon"),
        fillcolor="salmon",
        opacity=0.5
    )

# Add scatter for detailed hover
fig8.add_trace(go.Scatter(
    x=df['Sentiment'],
    y=[0] * len(df),
    mode='markers',
    marker=dict(color='rgba(0,0,0,0)', size=12),
    hovertemplate=
        "<b>Exact Sentiment:</b> %{x}<br>" +
        "<b>Title:</b> %{customdata[0]}<br>" +
        "<b>Author:</b> %{customdata[1]}<br>" +
        "<b>Link:</b> %{customdata[2]}<br><extra></extra>",
    customdata=df[['Title', 'Author', 'URL']]
))

fig8.update_layout(
    title="Sentiment Distribution of Question Titles",
    xaxis_title="Sentiment Polarity",
    yaxis_title="Count"
)

fig8.show()


# ============================================================
# End — All plots stay open
# ============================================================

input("Press Enter to close all plots...")
