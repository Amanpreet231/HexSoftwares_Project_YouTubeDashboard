# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

st.set_page_config(page_title="YouTube Data Dashboard", layout="wide")
st.title("📊 YouTube Data Dashboard ")

# ---------- Helpers ----------
@st.cache_data
def load_sample(csv_path="sample_videos.csv"):
    if not os.path.exists(csv_path):
        return pd.DataFrame()
    df = pd.read_csv(csv_path)
    if "published_at" in df.columns:
        df["published_at"] = pd.to_datetime(df["published_at"])
    else:
        df["published_at"] = pd.to_datetime("today")
    return df

@st.cache_data(ttl=3600)
def fetch_youtube_channel_videos(api_key: str, channel_id: str, max_results: int = 30):
    """
    Fetch recent videos (public data) for a channel using YouTube Data API v3.
    Returns a pandas DataFrame.
    Caches results for 1 hour (ttl=3600s).
    """
    try:
        youtube = build("youtube", "v3", developerKey=api_key)
        # 1) Get video IDs via search.list
        search_req = youtube.search().list(part="id", channelId=channel_id, maxResults=min(max_results,50), order="date", type="video")
        search_res = search_req.execute()
        video_ids = [item["id"]["videoId"] for item in search_res.get("items", [])]
        if not video_ids:
            return pd.DataFrame()  # no videos found
        # 2) Get video details via videos.list
        stats_req = youtube.videos().list(part="snippet,statistics", id=",".join(video_ids), maxResults=len(video_ids))
        stats_res = stats_req.execute()
        rows = []
        for v in stats_res.get("items", []):
            sn = v.get("snippet", {})
            stt = v.get("statistics", {})
            rows.append({
                "video_id": v.get("id"),
                "title": sn.get("title"),
                "published_at": sn.get("publishedAt")[:10] if sn.get("publishedAt") else None,
                "views": int(stt.get("viewCount", 0)) if stt.get("viewCount") else 0,
                "likes": int(stt.get("likeCount", 0)) if stt.get("likeCount") else 0,
                "comments": int(stt.get("commentCount", 0)) if stt.get("commentCount") else 0,
                "subscribers_gained": None,
                "watch_time_minutes": None,
                "category": None
            })
        df = pd.DataFrame(rows)
        if "published_at" in df.columns:
            df["published_at"] = pd.to_datetime(df["published_at"])
        return df
    except HttpError as e:
        st.error(f"YouTube API error: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Unexpected error fetching YouTube data: {e}")
        return pd.DataFrame()

# ---------- Sidebar: choose data source ----------
st.sidebar.header("Data Source")
source = st.sidebar.radio("Choose data source", ("Sample CSV (quick demo)", "YouTube API (public data)"))

if source == "Sample CSV (quick demo)":
    csv_path = st.sidebar.text_input("CSV file (path)", value="sample_videos.csv")
    df = load_sample(csv_path)
    if df.empty:
        st.sidebar.error("sample_videos.csv not found. Run generate_sample_data.py or put a CSV here.")
        st.stop()
else:
    st.sidebar.info("This fetches public video stats (views, likes, comments). You need an API key & channel ID.")
    api_key = st.sidebar.text_input("YouTube API Key", type="password")
    channel_id = st.sidebar.text_input("Channel ID (starts with UC...)")
    max_v = st.sidebar.slider("Max videos to fetch", 5, 50, 30)
    if not api_key or not channel_id:
        st.sidebar.warning("Enter API Key and Channel ID to fetch data.")
        st.stop()
    with st.spinner("Fetching data from YouTube..."):
        df = fetch_youtube_channel_videos(api_key.strip(), channel_id.strip(), max_results=max_v)
    if df.empty:
        st.error("No data returned. Check API key, channel ID, or API quota.")
        st.stop()

# ---------- Basic validation ----------
if "published_at" in df.columns:
    df["published_at"] = pd.to_datetime(df["published_at"])
else:
    df["published_at"] = pd.to_datetime("today")

# ---------- Filters ----------
st.sidebar.header("Filters")
min_default = df["published_at"].min().date() if not df.empty else datetime.today().date()
max_default = df["published_at"].max().date() if not df.empty else datetime.today().date()
min_date = st.sidebar.date_input("Start date", min_default)
max_date = st.sidebar.date_input("End date", max_default)
available_categories = df["category"].dropna().unique().tolist() if "category" in df.columns else []
selected_categories = st.sidebar.multiselect("Category (optional)", options=available_categories, default=available_categories)
metric = st.sidebar.selectbox("Primary metric", ["views", "likes", "comments", "watch_time_minutes", "subscribers_gained"])

# Apply filters
dff = df.copy()
dff = dff[(dff["published_at"].dt.date >= min_date) & (dff["published_at"].dt.date <= max_date)]
if available_categories and selected_categories:
    dff = dff[dff["category"].isin(selected_categories)]

# ---------- Top info cards ----------
st.markdown("## Overview")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Videos (filtered)", len(dff))
col2.metric("Total views", f"{int(dff['views'].sum()):,}" if "views" in dff.columns else "N/A")
col3.metric("Total likes", f"{int(dff['likes'].sum()):,}" if "likes" in dff.columns else "N/A")
col4.metric("Total comments", f"{int(dff['comments'].sum()):,}" if "comments" in dff.columns else "N/A")

# ---------- Top videos bar ----------
st.markdown("### 🎯 Top Videos by Selected Metric")
top_n = st.slider("Top N videos to show", 3, 20, 8)
if metric not in dff.columns:
    st.info(f"{metric} not available in dataset.")
else:
    top_df = dff.sort_values(by=metric, ascending=False).head(top_n)
    fig = px.bar(top_df, x="title", y=metric, hover_data=["views","likes","comments"], title=f"Top {top_n} videos by {metric}")
    fig.update_layout(xaxis_tickangle=-45, height=450)
    st.plotly_chart(fig, use_container_width=True)

# ---------- Time series ----------
st.markdown("### ⏱️ Weekly Time Series")
agg_metric = st.selectbox("Aggregate metric for time series", ["views", "likes", "comments"], index=0)
if agg_metric in dff.columns:
    ts = dff.set_index("published_at").resample("W")[agg_metric].sum().reset_index()
    fig2 = px.line(ts, x="published_at", y=agg_metric, markers=True, title=f"Weekly {agg_metric} over time")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Aggregate metric not available.")

# ---------- Scatter likes vs views ----------
st.markdown("### 🔎 Likes vs Views")
if "likes" in dff.columns and "views" in dff.columns:
    fig3 = px.scatter(dff, x="views", y="likes", hover_name="title", size="comments" if "comments" in dff.columns else None, title="Likes vs Views (size=comments)", log_x=True)
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("Likes or views missing for scatter plot.")

# ---------- Data table ----------
st.markdown("### 📋 Video Table")
show_cols = ["video_id","title","published_at","views","likes","comments","subscribers_gained","watch_time_minutes","category"]
available_cols = [c for c in show_cols if c in dff.columns]
st.dataframe(dff[available_cols].sort_values(by=metric, ascending=False).reset_index(drop=True))

# ---------- Per-video detail ----------
st.markdown("### Detail Viewer")
if not dff.empty:
    selected_title = st.selectbox("Select a video", dff["title"].tolist())
    row = dff[dff["title"] == selected_title].iloc[0]
    st.write("**Title:**", row.get("title"))
    st.write("**Published:**", row.get("published_at"))
    st.write("**Views:**", f"{int(row.get('views')):,}" if row.get('views') is not None else "N/A")
    st.write("**Likes:**", int(row.get('likes')) if row.get('likes') is not None else "N/A")
    st.write("**Comments:**", int(row.get('comments')) if row.get('comments') is not None else "N/A")
    st.write("**Watch time (min):**", row.get("watch_time_minutes"))
    st.write("**Subscribers gained:**", row.get("subscribers_gained"))
else:
    st.info("No videos to display with current filters.")
