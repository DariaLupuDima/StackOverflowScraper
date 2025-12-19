import sqlite3
import pandas as pd
import numpy as np
import html
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
from datetime import datetime
import webbrowser

from bokeh.plotting import figure
from bokeh.embed import file_html
from bokeh.resources import CDN
from bokeh.models import ColumnDataSource, HoverTool, TapTool, OpenURL
from bokeh.layouts import column
from bokeh.transform import linear_cmap
from bokeh.palettes import Oranges256, Blues256, Purples256, Viridis256

DB_PATH = "data/stack_questions.db"


# ============================================================
# LOAD DATA
# ============================================================
def load_data(keyword: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM questions WHERE keyword = ?"
    df = pd.read_sql_query(query, conn, params=[keyword])
    conn.close()
    return df


# ============================================================
# PREPARE DATAFRAME
# ============================================================
def prepare_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["Title"] = df["title"].apply(html.unescape)
    df["Author"] = df["author"]
    df["Score"] = df["score"]
    df["URL"] = df["url"]

    df["Title Length"] = df["Title"].apply(len)

    df["Short Title"] = df["Title"].apply(
        lambda x: x if len(x) <= 80 else x[:77] + "..."
    )

    # ✅ FIX: Bokeh-safe alias (NO spaces)
    df["ShortTitle"] = df["Short Title"]

    df["Sentiment"] = df["Title"].apply(lambda x: TextBlob(x).sentiment.polarity)

    if "creation_date" in df.columns:
        df["Creation Date"] = pd.to_datetime(df["creation_date"], errors="coerce")
        df["Creation Day"] = df["Creation Date"].dt.date

    # ⭐ HOTNESS METRIC
    df["Hotness"] = (
        df["Score"] * 1
        + df["answer_count"] * 2
        + df["view_count"] / 100
    )

    df = df.dropna(subset=["Title", "Author", "URL"])
    df = df[df["URL"] != ""]
    df = df.drop_duplicates(subset=["Title"], keep="first")

    # needed for Bokeh y-axis stability
    df["ShortShort"] = df["Short Title"].apply(
        lambda s: s[:50] + "..." if len(s) > 50 else s
    )

    return df


# ============================================================
# WORD CLOUD → image → HTML
# ============================================================
def generate_wordcloud_image(df: pd.DataFrame) -> str:
    text = " ".join(df["Title"].tolist())
    if not text.strip():
        return ""

    plt.switch_backend("Agg")
    wc = WordCloud(width=800, height=400, background_color="black").generate(text)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)

    import base64
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    return f"<img src='data:image/png;base64,{encoded}' style='max-width:100%; border-radius:10px;'>"


# ============================================================
# DARK THEME STYLING
# ============================================================
def style(p):
    p.background_fill_color = "#111111"
    p.border_fill_color = "#111111"
    p.outline_line_color = "#444"

    p.title.text_color = "white"
    p.xaxis.axis_label_text_color = "white"
    p.yaxis.axis_label_text_color = "white"
    p.xaxis.major_label_text_color = "#ddd"
    p.yaxis.major_label_text_color = "#ddd"

    p.xgrid.grid_line_color = "#333"
    p.ygrid.grid_line_color = "#333"

    return p


# ============================================================
# BOKEH PLOTS
# ============================================================
def plot_top_hot(df_hot):
    df = df_hot.sort_values("Hotness", ascending=False).head(5)
    if df.empty:
        return None
    df = df.iloc[::-1]

    source = ColumnDataSource(df)

    p = figure(
        y_range=list(df["ShortShort"]),
        width=900,
        height=350,
        title="🔥 Top 5 Hottest Questions",
        toolbar_location=None
    )

    mapper = linear_cmap("Hotness", Oranges256, df["Hotness"].min(), df["Hotness"].max())

    p.hbar(
        y="ShortShort",
        right="Hotness",
        height=0.6,
        source=source,
        fill_color=mapper,
        line_color=None
    )

    p.add_tools(HoverTool(tooltips=[
        ("Title", "@ShortTitle"),
        ("Hotness", "@Hotness{0.0}"),
        ("Open", "@URL")
    ]))

    p.add_tools(TapTool(callback=OpenURL(url="@URL")))

    p.xaxis.axis_label = "Hotness Score"
    p.yaxis.axis_label = "Question"
    return style(p)


def plot_longest(df_hot):
    df = df_hot.sort_values("Title Length", ascending=False).head(5)
    if df.empty:
        return None
    df = df.iloc[::-1]

    source = ColumnDataSource(df)

    p = figure(
        y_range=list(df["ShortShort"]),
        width=900,
        height=350,
        title="📏 Top 5 Longest Titles",
        toolbar_location=None
    )

    mapper = linear_cmap(
        "Title Length",
        Blues256,
        df["Title Length"].min(),
        df["Title Length"].max()
    )

    p.hbar(
        y="ShortShort",
        right="Title Length",
        height=0.6,
        source=source,
        fill_color=mapper,
        line_color=None
    )

    p.add_tools(HoverTool(tooltips=[
        ("Title", "@ShortTitle"),
        ("Length", "@{Title Length}"),
        ("Open", "@URL")
    ]))

    p.add_tools(TapTool(callback=OpenURL(url="@URL")))

    p.xaxis.axis_label = "Title Length"
    p.yaxis.axis_label = "Question"
    return style(p)


def plot_hotness_rank(df_hot):
    df = df_hot.sort_values("Hotness", ascending=False).head(15)
    if df.empty:
        return None
    df = df.iloc[::-1]

    source = ColumnDataSource(df)

    p = figure(
        y_range=list(df["ShortShort"]),
        width=900,
        height=700,
        title="🔥 Hotness Ranking (Top 15)",
        toolbar_location="above",
        tools="pan,wheel_zoom,reset"
    )

    mapper = linear_cmap("Hotness", Viridis256, df["Hotness"].min(), df["Hotness"].max())

    p.hbar(
        y="ShortShort",
        right="Hotness",
        height=0.55,
        source=source,
        fill_color=mapper,
        line_color=None
    )

    p.add_tools(HoverTool(tooltips=[
        ("Title", "@ShortTitle"),
        ("Hotness", "@Hotness{0.0}"),
        ("Open", "@URL")
    ]))

    p.add_tools(TapTool(callback=OpenURL(url="@URL")))

    p.xaxis.axis_label = "Hotness Score"
    p.yaxis.axis_label = "Question"
    return style(p)


def plot_sentiment(df_hot):
    source = ColumnDataSource(df_hot)

    p = figure(
        width=900,
        height=450,
        title="😊 Sentiment vs Hotness",
        tools="pan,wheel_zoom,reset",
        toolbar_location="above"
    )

    mapper = linear_cmap(
        "Hotness",
        Viridis256,
        df_hot["Hotness"].min(),
        df_hot["Hotness"].max()
    )

    p.circle(
        x="Sentiment",
        y="Hotness",
        size=8,
        source=source,
        fill_color=mapper,
        alpha=0.85,
        line_color=None
    )

    p.add_tools(HoverTool(tooltips=[
        ("Title", "@ShortShort"),
        ("Sentiment", "@Sentiment{0.00}"),
        ("Hotness", "@Hotness{0.0}"),
        ("Open", "@URL")
    ]))

    p.add_tools(TapTool(callback=OpenURL(url="@URL")))

    p.xaxis.axis_label = "Sentiment"
    p.yaxis.axis_label = "Hotness"
    return style(p)


def plot_title_length(df_hot):
    source = ColumnDataSource(df_hot)

    p = figure(
        width=900,
        height=450,
        title="📏 Title Length vs Hotness",
        tools="pan,wheel_zoom,reset",
        toolbar_location="above"
    )

    mapper = linear_cmap(
        "Hotness",
        Purples256,
        df_hot["Hotness"].min(),
        df_hot["Hotness"].max()
    )

    p.circle(
        x="Title Length",
        y="Hotness",
        size=8,
        source=source,
        fill_color=mapper,
        alpha=0.85,
        line_color=None
    )

    p.add_tools(HoverTool(tooltips=[
        ("Title", "@ShortShort"),
        ("Title Length", "@{Title Length}"),
        ("Hotness", "@Hotness{0.0}"),
        ("Open", "@URL")
    ]))

    p.add_tools(TapTool(callback=OpenURL(url="@URL")))

    p.xaxis.axis_label = "Title Length"
    p.yaxis.axis_label = "Hotness"
    return style(p)


def plot_time_series(df_hot):
    if "Creation Day" not in df_hot.columns:
        return None

    ts = df_hot.groupby("Creation Day").size().reset_index(name="Count")
    if ts.empty:
        return None

    source = ColumnDataSource(ts)

    p = figure(
        width=900,
        height=400,
        title="📅 Questions Over Time",
        x_axis_type="datetime",
        tools="pan,wheel_zoom,reset",
        toolbar_location="above"
    )

    p.line(x="Creation Day", y="Count", line_width=2, source=source)
    p.circle(x="Creation Day", y="Count", size=6, source=source)

    p.add_tools(HoverTool(
        tooltips=[
            ("Date", "@{Creation Day}{%F}"),
            ("Questions", "@Count")
        ],
        formatters={"@{Creation Day}": "datetime"}
    ))

    p.xaxis.axis_label = "Date"
    p.yaxis.axis_label = "Questions"
    return style(p)


# ============================================================
# MAIN: BUILD FULL REPORT
# ============================================================
def main():
    keyword = input("Enter keyword: ").strip()
    if not keyword:
        print("No keyword entered.")
        return

    df = load_data(keyword)
    if df.empty:
        print(f"No data found for '{keyword}'. Run scraper first.")
        return

    df = prepare_df(df)
    df_hot = df.sort_values("Hotness", ascending=False)

    print("Generating report...")

    plots = [
        plot_top_hot(df_hot),
        plot_longest(df_hot),
        plot_hotness_rank(df_hot),
        plot_sentiment(df_hot),
        plot_title_length(df_hot),
        plot_time_series(df_hot),
    ]

    plots = [p for p in plots if p is not None]

    wc_html = generate_wordcloud_image(df_hot)

    html_out = file_html(
        column(*plots),
        CDN,
        f"Hotness Report — {keyword}"
    )

    html_out = html_out.replace(
        "</body>",
        f"<hr><h2 style='color:white;'>Word Cloud — {keyword}</h2>{wc_html}</body>"
    )

    filename = f"report_{keyword}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_out)

    print(f"Report saved to {filename}")
    webbrowser.open(filename)


if __name__ == "__main__":
    main()
