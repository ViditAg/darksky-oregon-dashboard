# darksky-oregon-dashboard

## Project Overview

This project provides interactive dashboards for the Oregon Dark Sky SQM Network data, supporting three web frameworks:
- **Streamlit** (main dashboard, recommended)
- **Flask** (API and web dashboard)
- **Dash** (Dash/Plotly dashboard)

All data processing and visualization logic is modularized in `shared/utils/` and reused across all apps.

## Directory Structure

- `streamlit_app/` — Streamlit dashboard app (main entrypoint)
- `flask_api/` — Flask API and dashboard
- `dash_app/` — Dash/Plotly dashboard
- `shared/utils/` — Shared data processing and visualization modules
- `shared/data/` — Raw and processed data files
- `tests/` — Unit, integration, and performance tests

## Developer Guidance

- **Add new data/visualizations:**
	- Place new data files in `shared/data/`
	- Add or update processing logic in `shared/utils/data_processing.py`
	- Add or update visualization logic in `shared/utils/visualizations.py`
	- Use these shared functions in all app frontends
- **Run Streamlit app:**
	- `cd streamlit_app && streamlit run app.py`
- **Run Flask app:**
	- `cd flask_api && python app.py`
- **Run Dash app:**
	- `cd dash_app && python app.py`
- **Testing:**
	- Add tests in `tests/` and run with `pytest`

## Deployment Options

### Streamlit App
- **Streamlit Cloud (GitHub auto-deploy):**
	- Easiest, no infrastructure to manage
	- Push to GitHub, connect repo to Streamlit Cloud
	- Free for public projects, limited resources
- **Docker:**
	- Full control, can deploy anywhere (cloud VM, on-prem, etc.)
	- Requires Dockerfile, build, and host management

### Flask & Dash Apps
- **Docker:**
	- Recommended for consistency and portability
	- Can deploy to any cloud or on-prem
- **PaaS (Heroku, etc.):**
	- Add `Procfile` and requirements, deploy directly

## Contribution Guidelines
- Keep all data/visualization logic in `shared/utils/`
- UI code in each app should only handle layout and user interaction
- Write tests for new features
- Document major changes in this README

---
For questions, contact the maintainers or open an issue on GitHub.
