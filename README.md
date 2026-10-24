# Water Harvesting Tracker

A Flask web app to track rainwater harvesting. Add harvesting sites (roof area, runoff
coefficient, tank size), log rainfall and water usage, and see tank level, totals, overflow
waste and how many days the stored water will last.

## How it calculates
- Harvested litres = roof area (m²) x rainfall (mm) x runoff coefficient
- The tank is replayed in date order: rain fills it (anything beyond capacity is overflow wasted),
  usage drains it (demand beyond what is stored is counted as unmet demand)
- Days remaining = current level / average daily usage over the last 30 days

## Features
- Multiple sites with their own tank and roof settings
- Rainfall and usage logs with delete
- Dashboard: tank gauge, totals, monthly harvested vs used chart (no external libraries)
- Quick estimator for yearly harvest potential and a starting tank size
- REST API, `/health` endpoint, light/dark UI, seeded demo data (2 campus sites)

## Run locally
```
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py            # http://localhost:5000
python -m unittest discover tests
```

## API
| Method | Endpoint | Purpose |
|---|---|---|
| GET/POST | `/api/sites` | List / create site |
| DELETE | `/api/sites/<id>` | Delete site and its records |
| GET/POST | `/api/sites/<id>/rainfall` | List / log rainfall `{date, mm}` |
| GET/POST | `/api/sites/<id>/usage` | List / log usage `{date, litres, purpose}` |
| DELETE | `/api/rainfall/<id>`, `/api/usage/<id>` | Remove an entry |
| GET | `/api/sites/<id>/summary` | Tank level, totals, monthly stats |
| GET | `/api/estimate?area=&rainfall=&coeff=` | Yearly harvest estimate |
| GET | `/health` | Health check |

## Docker / deploy
```
docker build -t water-tracker .
docker run -d -p 80:8080 -v harvest-data:/data water-tracker
```
Runs on any VM (e.g. AWS EC2), Elastic Beanstalk (`Procfile`), Google Cloud Run or Render.
SQLite suits a demo; use a managed database for multiple instances.

## Possible extensions
Automatic rainfall from a weather API, water-quality log, sensor input from a tank level sensor, CSV export.
