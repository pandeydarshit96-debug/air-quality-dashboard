# Air Quality Monitoring Dashboard

A beginner-friendly Python + Streamlit application. No custom HTML, CSS,
JavaScript, separate backend, database, or simulated live data. Search defaults
to Jodhpur. All UI, requests, and application logic live in `app.py`.

## 1. API access (do this first)

This project uses the [World Air Quality Index Project JSON API](https://aqicn.org/api/).
Request your own token at <https://aqicn.org/data-platform/token/> and complete
the site's registration/email confirmation process. Never commit your token.

The API page currently describes free access with a valid token and quotas
(a default quota of 1,000 requests/second is advertised; do not treat this as a
guarantee of availability or your account's allocation). Review the current
terms when signing up and before deployment:

- Attribution to WAQI and the originating monitoring agency is mandatory.
  The dashboard displays the attribution supplied by each feed.
- Data cannot be sold, included in paid services, or redistributed as cached
  or archived data. This app does not persist or cache API readings.
- Public use by nonprofit organizations requires prior notification;
  public use by for-profit corporations requires explicit agreement.
  Confirm the applicable permission for a public college deployment.
- Station/city coverage, update frequency, and service uptime are not guaranteed.
  A valid city may have no feed. Jodhpur is the starting query, not a promise
  of coverage. Check the returned station; try a provider station identifier
  such as `@1234` only when you have found that actual identifier on WAQI.

Endpoint: `https://api.waqi.info/feed/{city}/?token=YOUR_TOKEN`.
The token is sent server-side over HTTPS and is never shown in error messages.

## 2. Local setup

Use Python 3.11 or newer. In PowerShell, from this project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` locally:

```toml
waqi_token = "your_actual_personal_token"
```

Then start the app (no virtual environment activation required):

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL printed by Streamlit, normally <http://localhost:8501>.
Select **Search**. On macOS/Linux, use `.venv/bin/python` instead of the Windows
Python path and `cp` instead of `Copy-Item`.

## 3. Understanding the readings

- The overall AQI and individual pollutant indices use WAQI's **US EPA AQI
  scale**, not India's National AQI. Categories are Good (0–50), Moderate
  (51–100), Unhealthy for Sensitive Groups (101–150), Unhealthy (151–200),
  Very Unhealthy (201–300), and Hazardous (above 300).
- `iaqi.pm25.v`, `iaqi.pm10.v`, etc. are **dimensionless pollutant AQI
  indices**, not raw concentrations. Weather fields are not pollutant indices
  and are not plotted. Only valid supplied pollutant numbers appear.
- Missing overall AQI has no category. Missing pollutant values are omitted,
  not replaced by zero. A true numeric zero is shown.
- The station name may describe a representative/nearby station rather than
  the entire city. The app shows monitoring-agency links when available.
- **Retrieval time** is when this app successfully received a feed, in UTC.
  **Observation time** is when the provider says the station reported it,
  with its time-zone offset. These are not interchangeable.
- Reports older than three hours are explicitly marked delayed. Three hours
  is a conservative application rule, not a WAQI freshness guarantee.
  Missing/unusable timestamps or future timestamps cannot verify freshness.
  Even recent reports are not instantaneous sensor measurements.
- This is a manually refreshed dashboard: click Search again to refresh.
  An open page remains a timestamped snapshot. Failed searches clear readings;
  only the previous successful retrieval timestamp remains in session state.
- General health advisories are not personalized medical advice. Provider
  measurements are provisional and can be revised.

## 4. Important functions

- `fetch_air_quality`: makes one HTTPS request with connection/read timeouts;
  translates connection, rate-limit, token, HTTP, and response errors into
  readable messages without exposing credentials.
- `valid_number`: rejects missing, negative, nonnumeric, and nonfinite data.
- `classify_aqi`: maps the reported AQI to its category and health advisory.
- `parse_readings`: extracts valid pollutant indices, station name, and the
  timezone-aware observation timestamp.
- The remaining code is the Streamlit UI: secrets, search form, metrics,
  chart, freshness warnings, and attribution, all in the same file.

A native Streamlit progress bar provides a simple 0–500 AQI gauge.

## 5. Tests and demonstration

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Tests use explicitly synthetic fixtures and mocked network responses; they
do not demonstrate live API availability and are never used by the dashboard.
They cover category boundaries, missing data, stale timestamps, request errors,
and Streamlit rendering, including clearing readings after a failed search.

For a real demonstration, configure your own token, search Jodhpur, check the
returned station and timestamps, and check the source attribution. Then try an
invalid city. If Jodhpur is unavailable, use a city with a confirmed WAQI feed.
Without a personal token, startup/tests can be verified but a real authenticated
live lookup cannot be certified. No fake fallback data is provided.

## 6. Upload to GitHub

Create an empty GitHub repository, then run from this project directory:

```powershell
git init
git add app.py requirements.txt README.md .gitignore .streamlit/secrets.toml.example tests
git status
git commit -m "Build Streamlit air quality dashboard"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

Replace the remote URL with your actual repository URL. Before committing,
confirm `.streamlit/secrets.toml` and `.venv` are not staged. `.gitignore`
excludes these; only the example secrets file should be tracked. If you ever
publish a token, revoke/rotate it immediately; deleting the file is not enough.

## 7. Deploy on Streamlit Community Cloud

1. Review WAQI's public-use terms and obtain any applicable permission first.
2. Sign in to <https://share.streamlit.io/> and connect your GitHub account.
3. Choose **Create app**, select your repository and `main` branch, and set
   the main file path to `app.py`.
4. In Advanced settings, choose Python 3.11 (or a compatible newer version).
5. Paste this into the app's **Secrets** settings, using your real token:

   ```toml
   waqi_token = "your_actual_personal_token"
   ```

6. Deploy. Cloud installs `requirements.txt`. Secrets are entered in Cloud,
   not uploaded to GitHub. You can change them later in the app settings.
7. Open the public app, perform a search, and check observation time and source
   attribution. Community Cloud's own resource/availability limits also apply.

## Troubleshooting

- **Missing token:** create the local secrets file or add Cloud secrets.
- **Invalid token/access denied:** check the account/token and provider terms.
- **Unknown city:** check spelling or use a confirmed WAQI station identifier.
- **Timeout/service error:** retry later; previous values will not be reused.
- **Rate limit:** wait before retrying. The app intentionally does not retry
  automatically or poll in the background.
- **Delayed timestamp:** the station has not supplied a recent report;
  repeatedly searching cannot force a sensor update.

