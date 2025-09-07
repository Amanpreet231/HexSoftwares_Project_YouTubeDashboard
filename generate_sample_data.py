# generate_sample_data.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)
n = 40
start = datetime.now() - timedelta(days=180)
dates = [start + timedelta(days=int(i)) for i in np.linspace(0, 180, n)]

data = {
    "video_id": [f"vid_{i}" for i in range(n)],
    "title": [f"Sample Video {i}" for i in range(n)],
    "published_at": [d.strftime("%Y-%m-%d") for d in dates],
    "views": np.random.randint(500, 50000, n),
    "likes": np.random.randint(10, 5000, n),
    "comments": np.random.randint(0, 500, n),
    "subscribers_gained": np.random.randint(0, 2000, n),
    "watch_time_minutes": np.random.randint(100, 40000, n),
    "category": np.random.choice(["Tech","Books","News","Entertainment"], n)
}

df = pd.DataFrame(data)
df.to_csv("sample_videos.csv", index=False)
print("✅ sample_videos.csv created successfully!")
