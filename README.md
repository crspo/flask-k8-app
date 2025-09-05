# Flask K8s App

This is a simple Python Flask application deployed to a self-hosted Kubernetes cluster using Helm.

## 🔧 Features

- Flask app with routes and templates
- Dockerized and deployed via Helm
- GitHub Actions CI/CD
- Self-hosted runner for local Kubernetes deployment

## 🚀 Project Structure

flask_project/
├── app.py
├── routes/
├── utils/
├── templates/
├── static/
├── helm/
└── .github/workflows/


## 📦 Deployment

- Docker builds app image
- GitHub Actions deploys to local Kubernetes via Helm
- Ingress is used for public access (with optional TLS)

