# YouTube Data Dashboard (Streamlit)

📊 **YouTube Data Dashboard** — an interactive Streamlit app to visualize YouTube channel metrics using a demo CSV or live YouTube Data API v3.

---

## 🚀 Project summary
**YouTube Data Dashboard** is a lightweight Streamlit app that helps you explore a channel’s public metrics:

- Top videos by views / likes / comments
- Weekly time-series of metrics
- Likes vs Views scatter plot for outlier detection
- Video thumbnails (sample placeholders or real YouTube thumbnails)
- Filterable table and per-video detail view
- Export filtered data to CSV

This project was built as part of an internship/task submission and is ideal for quick analysis and demos.

---

## 🧰 Tech stack
- Python 3.8+
- Streamlit — web UI
- pandas — data handling
- plotly.express — interactive charts
- google-api-python-client — YouTube Data API (optional, live mode)
- python-dotenv — optional (.env support)

---

## 📁 Repository structure
yt-dashboard/
├── app.py # main Streamlit app
├── generate_sample_data.py # creates sample_videos.csv (with thumbnails)
├── sample_videos.csv # generated demo CSV (optional)
├── requirements.txt
├── README.md


---## ⚡ Quick start (demo mode)
1. Create & activate a virtual environment (PowerShell):
powershell
python -m venv venv
.\venv\Scripts\Activate.ps1


Install dependencies:

powershell
pip install -r requirements.txt
Generate sample data (creates sample_videos.csv with placeholder thumbnails):

powershell
python generate_sample_data.py
Run the app:

powershell
streamlit run app.py
Open http://localhost:8501 (Streamlit opens it automatically).

🔌 Run with YouTube Data API (live data)
When you want to fetch real channel data:

Create a Google Cloud project and enable YouTube Data API v3. Create an API key in the console.

In the app sidebar choose YouTube API (public data), paste:

YouTube API Key (or set it as YOUTUBE_API_KEY in your environment / .env)

Channel ID / URL / Handle — the app accepts UC... ids, a channel URL and will try to resolve it.

Set Max videos and click fetch. The dashboard will populate with live stats & thumbnails.

Note: The app fetches only public metadata and basic stats (views / likes / comments). For detailed analytics (watch time by date, traffic sources) you must use YouTube Analytics API with OAuth and channel-owner permission.

🛠️ Customization & extensions

Ideas to extend the dashboard:

Add YouTube Analytics OAuth flow to pull watch-time & traffic source reports.

Show engagement rates (likes/views) and moving averages.

Add automated daily data fetching and store in a database (BigQuery / SQLite).

Add thumbnail analysis (auto-pick best thumbnail using image features).

🧾 Troubleshooting

ModuleNotFoundError: ensure your virtual env is active and you installed packages from requirements.txt.

YouTube API error or empty results: check Channel ID (must resolve to UC...), API key permissions, and API quota.

Streamlit not auto-refreshing: save your file or restart streamlit run app.py.

🔗 Links & contact

Author: Amanpreet
GitHub: github.com/Amanpreet231
LinkedIn: www.linkedin.com/in/amanpreet-singh-bhatia-093370204

📜 License

This repository is provided for learning/demonstration purposes. Feel free to reuse and adapt the code for personal projects. If you want a license, add one (e.g., MIT) and update this README.
