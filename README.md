# Oregon Dark Sky Dashboard

Interactive dashboards to visualize **Night Sky Brightness** based on the [Oregon Dark Sky Oregon SQM Network data](https://www.darkskyoregon.org/blog/darksky-oregon-sqm-network-tech-report-dec-2024):
- **Streamlit**: Simple, fast, and cloud-friendly dashboard. [Live Demo](https://darksky-oregon-dashboard.streamlit.app/)
- **Dash**: Advanced dashboard with Plotly interactivity. [Live Demo](https://darksky-oregon-dashboard.onrender.com/)

Click on the live demo link to go to the dashboard. Here is a [userguide](./docs/user_guide/README.md) to make the best use of these dashboards

## Directory Structure
- `dash_app/` — Dash dashboard
- `streamlit_app/` — Streamlit dashboard
- `shared/utils/` — Shared data processing and visualization modules
- `shared/data/` — Raw and processed data files
- `tests/` — Unit, integration, and performance tests
- `docker/` — Dockerfiles for each app


## Prerequisites

- **Python 3.8+** (Download from [python.org](https://www.python.org/downloads/))
- **Git** (Download from [git-scm.com](https://git-scm.com/downloads))  
- **For Windows users**: We recommend using Git Bash (included with Git) or Windows Subsystem for Linux (WSL) for the best experience with shell commands.

## Contribution Guidelines

To contribute to this project:

1. **Fork and Clone**
   - Fork the repository on GitHub.
   - Clone your fork:
     ```bash
     git clone https://github.com/<your-username>/darksky-oregon-dashboard.git
     cd darksky-oregon-dashboard
     ```
   - Note: These commands work the same on Windows Command Prompt, PowerShell, and Git Bash.

2. **Set Up Local Development Environment**
   
   **For Linux/macOS:**
   - Use the provided setup script:
     ```bash
     chmod +x setup_env.sh
     ./setup_env.sh
     source venv_dashboard/bin/activate
     ```
   
   **For Windows:**
   - Create and activate a virtual environment manually:
     ```cmd
     python -m venv venv_dashboard
     venv_dashboard\Scripts\activate
     pip install -r requirements.txt
     ```
   
   - This creates and activates a virtual environment for you.

3. **Make Your Edits**
   - Edit code and add new features or bug fixes.
   - Add or update accompanying tests in `tests/unit/`.

4. **Run Apps Locally**
   Make sure you are in the project root folder. 
   - Streamlit
   ```bash
   streamlit run streamlit_app/app.py
   ```
   **App will be available at http://localhost:8501/**
   - Dash
   ```bash
   python dash_app/app.py
   ```
   **App will be available at http://localhost:8050/**
   

5. **Run Tests Locally**
   ```bash
   python -m unittest tests.unit.test_data_processing # run tests for data processing only
   python -m unittest tests.unit.test_visualizations # run tests for visualizations only
   python -m unittest tests.unit.test_streamlit_app # run Streamlit dashboard tests only
   python -m unittest tests.unit.test_dash_app # run Dash dashboard tests only
   python -m unittest discover -s tests/unit # run all the tests 
   ```

6. **Run Docker Compose for Apps and Tests**
   - Build and run a app:
   ```bash
   # replace streamlit with dash to run other app
   docker compose build streamlit
   docker compose up streamlit
   ```
   - Run tests for the respective module where edits are made:
   ```bash
   docker compose --profile test up test-data-processing # run tests for data processing only
   docker compose --profile test up test-visualizations # run tests for visualizations only
   docker compose --profile test up test-dash # run Dash dashboard tests only
   docker compose --profile test up test-streamlit # run Streamlit dashboard tests only
   docker compose --profile test up # run all test services defined under the 'test' profile
   ```

7. **Create a Pull Request**
   - Push your changes to your fork.
   - Open a pull request to the `main` branch of the original repository.
   - Provide enough detail for reviewers to understand the motivation and impact of your edits.

**Note:** Please ensure all tests pass locally before submitting your pull request. Automated tests will run on GitHub Actions via `.github/workflows/python-tests.yml` when any pull request is opened or merged to `main`.

## Data Swap & CSV Editing Guidelines

As we get more data collected, we need to update or swap CSV data files in `shared/data/`. Since adding new data can potentially impact all 3 dashboards:
- Follow the contributor guide to create a local copy of this repository.
- Ensure new files match the expected format (column names, types, and structure).
- Document any changes to the data format in the commit message and README.
- Run all apps and tests locally after making data changes to verify compatibility.
- If you add new columns or change structure, update shared/utils/data_processing.py and related tests.
- If needed, add or update tests in `tests/unit/` to validate data loading and processing with the new CSVs.

# Deployment Guide

## Local Docker Deployment
- Build and run any app using Docker Compose:
  ```bash
  docker-compose build dash  # or streamlit
  docker-compose up dash     # or streamlit
  ```
- See `docker/` folder for Dockerfiles and per-app README files.

## Cloud Deployment
- **Streamlit Cloud:**
  - Connect your GitHub repo at https://streamlit.io/cloud
  - Free for public projects, quick setup
- **Render.com:**
  - Connect your GitHub repo at https://dashboard.render.com
  - Choose Python web service or Docker
  - Deploy using the repository's Dockerfile
  - Free tier: 750 hours/month per app

## Environment Variables
- For Docker, environment variables are set in `docker-compose.yml`

## CI/CD
- GitHub Actions can automate testing and deployment
- See `.github/workflows/` for example workflows