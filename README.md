# 🛒 Walmart Sales Forecasting API
Production-ready Machine Learning pipeline for **weekly retail sales forecasting**.

This project builds an end-to-end ML system that:
- trains a time-series forecasting model
- serves predictions through a FastAPI REST API
- runs inside Docker containers
- deploys automatically to Google Cloud Run
- updates automatically via CI/CD when pushing to GitHub

---

## 🌐 Live Demo (Cloud Deployment)

Public Swagger Docs:

https://sales-forecast-api-375373339806.me-central1.run.app/docs

You can test directly in the browser.

---

## 🚀 What this project demonstrates

This is not just a model — it's a **production ML system**.

It covers:

- Time-series feature engineering
- Model training & validation
- Model serialization
- REST API serving
- Docker containerization
- Cloud deployment
- CI/CD automation (GitHub → Cloud Build → Cloud Run)

---

## 📊 Notebook (Model Development)

All modeling was done inside the notebook.

### Steps performed:

### Data preparation
- merged historical sales + store info + macro data
- handled missing promotions (MarkDown → 0)
- encoded categorical store types
- converted dates to time features

### Feature engineering
Created time-series features:

- week, month, year
- is_weekend
- lag_1, lag_2, lag_4, lag_8
- rolling means (4 weeks, 8 weeks)

These allow the model to:
- capture seasonality
- learn trends
- use previous weeks as signals

### Model training
- XGBoost Regressor
- train/validation split
- evaluation using MAE

### Results
Validation MAE:

~1518 weekly sales

## 📦 Model Artifacts

After training in the notebook, the following files are exported:

artifacts/model.joblib  
artifacts/metadata.json  
data/history.parquet  

These files are loaded by the API during startup to enable real-time predictions.

## 🧠 How Prediction Works

When a request hits the API:

1. Historical sales are loaded
2. Lag + rolling features are generated dynamically
3. A feature vector is constructed
4. The trained model predicts next week's sales
5. JSON response is returned

All of this happens in milliseconds.

## 🔌 API Endpoints

## Health Check

GET /health

### Response
```json
{
  "status": "ok"
}
```
## Model Info

GET /model-info

### Returns:
- number of features
- validation MAE
- metadata


## Earliest Valid Date

GET /earliest-valid-date?store=1&dept=1

### Returns
- the first date that has enough historical weeks to compute lag features.


## Compare Prediction with Actual

GET /compare-next-week?store=1&dept=1&date=2010-08-06

### Returns
```json
{
  "y_true_next_week": 15536.4,
  "yhat_next_week": 15806.66,
  "abs_error": 270.26
}
```


## Forecast Next Week

POST /forecast-next-week

### Request
```json
{
  "store": 1,
  "dept": 1,
  "date": "2010-08-06"
}
```
### Response
```json
{
  "yhat_weekly_sales": 15806.66
}
```


## 🐳 Docker

Run the API locally using Docker.  
This guarantees the same environment as production.

### Build the Docker image

```bash
docker build -t sales-forecast-api .
```
### Run the Container

```bash
docker run --rm -p 8000:8000 sales-forecast-api
```


### Run with container name

```bash
docker run --name sales-api -p 8000:8000 sales-forecast-api
```

## ☁️ Cloud Deployment (Google Cloud Run)

### What happens during deployment
- Docker image is built
- Image stored in Artifact Registry
- Container deployed to Cloud Run
- Auto scaling enabled
- Public HTTPS endpoint generated

### Benefits
- No servers to manage
- Automatic scaling
- Pay only when used
- Fast startup
- Production ready


## 🔁 CI/CD Pipeline
### Every GitHub push automatically:

- builds Docker image
- pushes image to Artifact Registry
- deploys a new Cloud Run revision

### Deploy Command
```bash
git push
```


---

# 📁 Project Structure

```markdown
## 📁 Project Structure
api/        → FastAPI server
core/       → feature engineering + loaders
data/       → history dataset
artifacts/  → trained model files
notebook/   → training notebook
Dockerfile
cloudbuild.yaml
```

## 🛠 Tech Stack
- Python
- Pandas
- XGBoost
- FastAPI
- Docker
- Google Cloud Run
- Cloud Build (CI/CD)


## 🎯 Why This Project Matters

This project demonstrates:

- ML engineering
- MLOps
- Production APIs
- Cloud deployment
- Automation

It simulates how real companies deploy machine learning systems into production.

Not just a notebook — a complete ML system.


## 👤 Author

### Omar Abdelwahab  
#### Data Scientist | MLOps | Machine Learning Engineer

#### Designed and deployed this end-to-end ML forecasting system:
#### training → API → Docker → Cloud Run → CI/CD → production.
