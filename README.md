# 🌬️ Air Quality Monitoring Dashboard

A real-time air quality dashboard built with Python and Streamlit. Search any city and get live AQI data powered by the [World Air Quality Index (WAQI) API](https://aqicn.org/).

![Python](https://img.shields.io/badge/Python-3.11+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red) ![License](https://img.shields.io/badge/License-MIT-green)

---

## 🚀 Live Demo

👉 [View on Streamlit Cloud](https://share.streamlit.io)

---

## ✨ Features

- 🔍 Search any city worldwide for live AQI data
- 📊 Overall AQI with US EPA scale classification (Good → Hazardous)
- 🧪 Individual pollutant readings — PM2.5, PM10, O3, NO2, SO2, CO
- 📈 Bar chart and AQI gauge visualization
- 🕒 Station observation timestamp with freshness warning (>3 hrs)
- 📡 Data source attribution from monitoring agencies
- 🔒 API token handled securely via Streamlit secrets

---

## 🗂️ Project Structure

```
air-quality-dashboard/
├── app.py                          # Main Streamlit app (all logic + UI)
├── requirements.txt                # Python dependencies
├── .streamlit/
│   └── secrets.toml.example        # Template for API token
└── .gitignore
```

---

## ⚙️ Local Setup

**1. Clone the repo**
```bash
git clone https://github.com/pandeydarshit96-debug/air-quality-dashboard.git
cd air-quality-dashboard
```

**2. Create virtual environment and install dependencies**
```bash
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**3. Add your WAQI API token**

Get a free token from [aqicn.org/data-platform/token](https://aqicn.org/data-platform/token/), then:
```bash
copy .streamlit\secrets.toml.example .streamlit\secrets.toml
```
Edit `.streamlit/secrets.toml`:
```toml
waqi_token = "your_actual_token_here"
```

**4. Run the app**
```bash
.\.venv\Scripts\python.exe -m streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501)

---

## ☁️ Deploy on Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **Create app** → select this repo → set main file to `app.py`
4. In **Advanced settings** → add secret:
   ```toml
   waqi_token = "your_actual_token_here"
   ```
5. Click **Deploy**

---

## 📖 AQI Scale (US EPA)

| AQI Range | Category | Who's Affected |
|-----------|----------|----------------|
| 0–50 | ✅ Good | None |
| 51–100 | ⚠️ Moderate | Unusually sensitive people |
| 101–150 | ⚠️ Unhealthy for Sensitive Groups | Sensitive groups |
| 151–200 | ❌ Unhealthy | Everyone |
| 201–300 | ☠️ Very Unhealthy | Everyone — limit outdoor activity |
| 301+ | ☠️ Hazardous | Everyone — avoid outdoor activity |

---

## 🔧 Tech Stack

- **[Streamlit](https://streamlit.io/)** — UI and app framework
- **[WAQI API](https://aqicn.org/api/)** — Real-time air quality data
- **[Requests](https://docs.python-requests.org/)** — HTTP requests

---

> ⚠️ Readings are provisional. Health advisories are general and not personalized medical advice.
