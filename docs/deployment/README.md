<!--
This folder contains instructions for deploying the Oregon Dark Sky Dashboard apps.

- Docker: See docker-compose.yml and Dockerfiles for local and production deployment.
- Cloud: Add cloud-specific deployment steps (AWS, GCP, Azure, Render, Streamlit Cloud) as needed.
- Environment Variables: Document required variables for each app.
-->

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
  - Connect your repo, choose Python web service or Docker
  - Deploy using the repository's Dockerfile
  - Free tier: 750 hours/month per app

## Environment Variables
- For Docker, environment variables are set in `docker-compose.yml`

## CI/CD
- GitHub Actions can automate testing and deployment
- See `.github/workflows/` for example workflows
