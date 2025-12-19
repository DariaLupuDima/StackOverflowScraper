from flask import Flask, render_template, request
import sqlite3
import pandas as pd
import html
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64

from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, TapTool, OpenURL
from bokeh.transform import linear_cmap
from bokeh.palettes import Oranges256, Blues256, Purples256, Viridis256

DB_PATH = "data/stack_questions.db"

app = Flask(__name__)


# ============================================================
# DB HELPERS
# ============================================================
def load_data(keyword: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM questions WHERE keyword = ?"
    df = pd.read_sql_query(query, conn, params=[keyword])
    conn.close()
    return df


def get_keyword_history(limit: int = 30):
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT keyword, MAX(scraped_at) AS last_seen
        FROM questions
        GROUP BY keyword
        ORDER BY datetime(last_seen) DESC
        LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=[limit])
    conn.close()
    return df["keyword"].tolist()


# ============================================================
# DATA PREP
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

    df["Sentiment"] = df["Title"].apply(
        lambda x: TextBlob(x).sentiment.polarity
    )

    if "creation_date" in df.columns:
        df["Creation Date"] = pd.to_datetime(
            df["creation_date"], errors="coerce"
        )
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

    # short label for axes
    df["ShortShort"] = df["Short Title"].apply(
        lambda s: s[:50] + "..." if len(s) > 50 else s
    )

    return df


# ============================================================
# WORD CLOUD
# ============================================================
def generate_wordcloud(df: pd.DataFrame) -> str:
    text = " ".join(df["Title"].tolist())
    if not text.strip():
        return ""

    plt.switch_backend("Agg")
    wc = WordCloud(
        width=800, height=400, background_color="black"
    ).generate(text)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)

    encoded = base64.b64encode(buf.read()).decode("utf-8")
    return encoded


# ============================================================
# BOKEH STYLING
# ============================================================
def style_figure(p):
    p.background_fill_color = "#111111"
    p.border_fill_color = "#111111"
    p.outline_line_color = "#444444"

    p.title.text_color = "#ffffff"
    p.xaxis.axis_label_text_color = "#ffffff"
    p.yaxis.axis_label_text_color = "#ffffff"
    p.xaxis.major_label_text_color = "#dddddd"
    p.yaxis.major_label_text_color = "#dddddd"

    p.xgrid.grid_line_color = "#333333"
    p.ygrid.grid_line_color = "#333333"

    return p


# ============================================================
# BOKEH CHART BUILDERS (return FIGURES)
# ============================================================
def bokeh_top_hot(df_hot, label):
    df = df_hot.sort_values("Hotness", ascending=False).head(5)
    if df.empty:
        return None
    df = df.iloc[::-1]

    source = ColumnDataSource(df)

    p = figure(
        y_range=list(df["ShortShort"]),
        height=350,
        width=900,
        title=f"🔥 Top 5 Hottest Questions — {label}",
        toolbar_location=None,
    )

    mapper = linear_cmap(
        "Hotness",
        Oranges256,
        float(df["Hotness"].min()),
        float(df["Hotness"].max()),
    )

    p.hbar(
        y="ShortShort",
        right="Hotness",
        height=0.6,
        source=source,
        fill_color=mapper,
        line_color=None,
    )

    p.add_tools(
        HoverTool(
            tooltips=[
                ("Title", "@ShortTitle"),
                ("Hotness", "@Hotness{0.0}"),
                ("Open", "@URL"),
            ]
        )
    )
    tap = TapTool()
    tap.callback = OpenURL(url="@URL")
    p.add_tools(tap)

    p.xaxis.axis_label = "Hotness Score"
    p.yaxis.axis_label = "Question"
    return style_figure(p)


def bokeh_longest_titles(df_hot, label):
    df = df_hot.sort_values("Title Length", ascending=False).head(5)
    if df.empty:
        return None
    df = df.iloc[::-1]

    source = ColumnDataSource(df)

    p = figure(
        y_range=list(df["ShortShort"]),
        height=350,
        width=900,
        title=f"📏 Top 5 Longest Titles — {label}",
        toolbar_location=None,
    )

    mapper = linear_cmap(
        "Title Length",
        Blues256,
        float(df["Title Length"].min()),
        float(df["Title Length"].max())
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

    tap = TapTool()
    tap.callback = OpenURL(url="@URL")
    p.add_tools(tap)

    p.xaxis.axis_label = "Title Length"
    p.yaxis.axis_label = "Question"

    return style_figure(p)


def bokeh_hotness_ranking(df_hot, label):
    df = df_hot.sort_values("Hotness", ascending=False).head(15)
    if df.empty:
        return None
    df = df.iloc[::-1]

    source = ColumnDataSource(df)

    p = figure(
        y_range=list(df["ShortShort"]),
        height=750,
        width=900,
        title=f"🔥 Hotness Ranking (Top 15) — {label}",
        toolbar_location="above",
        tools="pan,wheel_zoom,reset",
    )

    mapper = linear_cmap(
        "Hotness",
        Viridis256,
        float(df["Hotness"].min()),
        float(df["Hotness"].max()),
    )

    p.hbar(
        y="ShortShort",
        right="Hotness",
        height=0.55,
        source=source,
        fill_color=mapper,
        line_color=None,
    )

    p.add_tools(
        HoverTool(
            tooltips=[
                ("Title", "@ShortTitle"),
                ("Hotness", "@Hotness{0.0}"),
                ("Open", "@URL"),
            ]
        )
    )
    tap = TapTool()
    tap.callback = OpenURL(url="@URL")
    p.add_tools(tap)

    p.xaxis.axis_label = "Hotness Score"
    p.yaxis.axis_label = "Question"
    return style_figure(p)


def bokeh_authors(df_hot, label):
    df = df_hot["Author"].value_counts().head(5).reset_index()
    if df.empty:
        return None
    df.columns = ["Author", "Count"]
    df = df.iloc[::-1]

    source = ColumnDataSource(df)

    p = figure(
        y_range=list(df["Author"]),
        height=350,
        width=600,
        title=f"👤 Top 5 Authors — {label}",
        toolbar_location=None,
    )

    mapper = linear_cmap(
        "Count",
        Purples256,
        int(df["Count"].min()),
        int(df["Count"].max()),
    )

    p.hbar(
        y="Author",
        right="Count",
        height=0.6,
        source=source,
        fill_color=mapper,
        line_color=None,
    )

    p.add_tools(HoverTool(tooltips=[("Author", "@Author"), ("Count", "@Count")]))
    p.xaxis.axis_label = "Questions"
    p.yaxis.axis_label = "Author"
    return style_figure(p)


def bokeh_sentiment_vs_hotness(df_hot, label):
    if df_hot.empty:
        return None

    source = ColumnDataSource(df_hot)

    p = figure(
        height=450,
        width=900,
        title=f"😊 Sentiment vs Hotness — {label}",
        toolbar_location="above",
        tools="pan,wheel_zoom,reset",
    )

    mapper = linear_cmap(
        "Hotness",
        Viridis256,
        float(df_hot["Hotness"].min()),
        float(df_hot["Hotness"].max()),
    )

    p.circle(
        x="Sentiment",
        y="Hotness",
        size=8,
        source=source,
        fill_color=mapper,
        alpha=0.85,
        line_color=None,
    )

    p.add_tools(
        HoverTool(
            tooltips=[
                ("Title", "@ShortShort"),
                ("Sentiment", "@Sentiment{0.00}"),
                ("Hotness", "@Hotness{0.0}"),
                ("Open", "@URL"),
            ]
        )
    )
    tap = TapTool()
    tap.callback = OpenURL(url="@URL")
    p.add_tools(tap)

    p.xaxis.axis_label = "Sentiment"
    p.yaxis.axis_label = "Hotness"
    return style_figure(p)


def bokeh_titlelen_vs_hotness(df_hot, label):
    if df_hot.empty:
        return None

    source = ColumnDataSource(df_hot)

    p = figure(
        height=450,
        width=900,
        title=f"📏 Title Length vs Hotness — {label}",
        toolbar_location="above",
        tools="pan,wheel_zoom,reset",
    )

    mapper = linear_cmap(
        "Hotness",
        Purples256,
        float(df_hot["Hotness"].min()),
        float(df_hot["Hotness"].max()),
    )

    p.circle(
        x="Title Length",
        y="Hotness",
        size=8,
        source=source,
        fill_color=mapper,
        alpha=0.85,
        line_color=None,
    )

    p.add_tools(
        HoverTool(
            tooltips=[
                ("Title", "@ShortShort"),
                ("Length", "@{Title Length}"),
                ("Hotness", "@Hotness{0.0}"),
                ("Open", "@URL"),
            ]
        )
    )
    tap = TapTool()
    tap.callback = OpenURL(url="@URL")
    p.add_tools(tap)

    p.xaxis.axis_label = "Title Length"
    p.yaxis.axis_label = "Hotness"
    return style_figure(p)


def bokeh_time_series(df_hot, label):
    if "Creation Day" not in df_hot.columns:
        return None
    ts = df_hot.groupby("Creation Day").size().reset_index(name="Count")
    if ts.empty:
        return None

    source = ColumnDataSource(ts)

    p = figure(
        height=400,
        width=900,
        title=f"📅 Questions Over Time — {label}",
        x_axis_type="datetime",
        toolbar_location="above",
        tools="pan,wheel_zoom,reset",
    )

    p.line(x="Creation Day", y="Count", source=source, line_width=2)
    p.circle(x="Creation Day", y="Count", source=source, size=6)

    p.add_tools(
        HoverTool(
            tooltips=[
                ("Date", "@{Creation Day}{%F}"),
                ("Questions", "@Count"),
            ],
            formatters={"@{Creation Day}": "datetime"},
        )
    )

    p.xaxis.axis_label = "Date"
    p.yaxis.axis_label = "Questions"
    return style_figure(p)


def bokeh_tags(df_hot, label):
    tags = df_hot["tags"].dropna().str.split(",").explode()
    if tags.empty:
        return None

    counts = tags.value_counts().head(10).reset_index()
    counts.columns = ["Tag", "Count"]

    source = ColumnDataSource(counts)

    p = figure(
        x_range=list(counts["Tag"]),
        height=350,
        width=900,
        title=f"🏷️ Top 10 Tags — {label}",
        toolbar_location="above",
        tools="pan,wheel_zoom,reset",
    )

    mapper = linear_cmap(
        "Count",
        Blues256,
        int(counts["Count"].min()),
        int(counts["Count"].max()),
    )

    p.vbar(
        x="Tag",
        top="Count",
        width=0.7,
        source=source,
        fill_color=mapper,
        line_color=None,
    )

    p.add_tools(HoverTool(tooltips=[("Tag", "@Tag"), ("Count", "@Count")]))
    p.xaxis.axis_label = "Tag"
    p.yaxis.axis_label = "Occurrences"
    return style_figure(p)


# ============================================================
# WRAP FIGURES → {script, div}
# ============================================================
def wrap_plot(fig):
    if fig is None:
        return None
    script, div = components(fig)
    return {"script": script, "div": div}


# ============================================================
# COMBINE ALL PLOTS FOR ONE KEYWORD
# ============================================================
def build_keyword_plots(df: pd.DataFrame, label: str):
    df_hot = df.sort_values("Hotness", ascending=False)

    return {
        "top_hot": wrap_plot(bokeh_top_hot(df_hot, label)),
        "longest": wrap_plot(bokeh_longest_titles(df_hot, label)),
        "authors": wrap_plot(bokeh_authors(df_hot, label)),
        "hot_rank": wrap_plot(bokeh_hotness_ranking(df_hot, label)),
        "sentiment": wrap_plot(bokeh_sentiment_vs_hotness(df_hot, label)),
        "titlelen": wrap_plot(bokeh_titlelen_vs_hotness(df_hot, label)),
        "time_series": wrap_plot(bokeh_time_series(df_hot, label)),
        "tags": wrap_plot(bokeh_tags(df_hot, label)),
        "wordcloud": generate_wordcloud(df_hot),
    }


# ============================================================
# ROUTE
# ============================================================
@app.route("/", methods=["GET", "POST"])
def dashboard():
    keyword = ""
    compare = ""
    msg = None

    history = get_keyword_history()
    main = {}
    cmp = {}

    if request.method == "POST":
        kw_input = request.form.get("keyword", "").strip()
        kw_hist = request.form.get("keyword_history", "").strip()

        keyword = kw_input or kw_hist
        compare = request.form.get("compare_keyword", "").strip()

        if not keyword:
            msg = "Please enter or select a keyword."
        else:
            df = load_data(keyword)
            if df.empty:
                msg = f"No data for '{keyword}'. Run scraper first."
            else:
                df = prepare_df(df)
                main = build_keyword_plots(df, keyword)

                if compare:
                    dfc = load_data(compare)
                    if dfc.empty:
                        msg = f"No data for compare keyword '{compare}'."
                        compare = ""
                    else:
                        dfc = prepare_df(dfc)
                        cmp = build_keyword_plots(dfc, compare)

    return render_template(
        "dashboard.html",
        keyword=keyword,
        compare_keyword=compare,
        msg=msg,
        history=history,
        main=main,
        compare=cmp,
    )


# ============================================================
# RUN FLASK
# ============================================================
if __name__ == "__main__":
    app.run(debug=True)
