# Datasets Reference & Setup Guide

This directory contains the data architecture used for training the machine learning models in the **Multi-Disease Risk Prediction (MDRP)** system.

> [!NOTE]
> In accordance with privacy and repository best practices, raw and processed CSV datasets (`data/raw/*.csv` and `data/processed/*.csv`) are not stored directly in the Git repository. You can acquire the public benchmark datasets directly from the verified sources listed below.

---

## Dataset Sources & Download Links

### 1. Diabetes Dataset
- **Target File**: `data/raw/diabetes.csv`
- **Source**: National Institute of Diabetes and Digestive and Kidney Diseases (Pima Indians Diabetes Database)
- **Primary Download Links**:
  - [UCI Machine Learning Repository - Diabetes](https://archive.ics.uci.edu/dataset/34/diabetes)
  - [Kaggle - Pima Indians Diabetes Database](https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database)
- **Key Features**: `Pregnancies`, `Glucose`, `BloodPressure`, `SkinThickness`, `Insulin`, `BMI`, `DiabetesPedigreeFunction`, `Age`, `Outcome`

---

### 2. Heart Disease Dataset
- **Target File**: `data/raw/heart.csv`
- **Source**: Cleveland Heart Disease Database (UCI / David W. Aha)
- **Primary Download Links**:
  - [UCI Machine Learning Repository - Heart Disease](https://archive.ics.uci.edu/dataset/45/heart+disease)
  - [Kaggle - Heart Disease Dataset](https://www.kaggle.com/datasets/johnsmith88/heart-disease-dataset)
- **Key Features**: `age`, `sex`, `cp`, `trestbps`, `chol`, `fbs`, `restecg`, `thalach`, `exang`, `oldpeak`, `slope`, `ca`, `thal`, `target`

---

### 3. Chronic Kidney Disease (CKD) Dataset
- **Target File**: `data/raw/kidney.csv`
- **Source**: Apollo Hospitals / UCI Machine Learning Repository
- **Primary Download Links**:
  - [UCI Machine Learning Repository - Chronic Kidney Disease](https://archive.ics.uci.edu/dataset/336/chronic_kidney_disease)
  - [Kaggle - Chronic Kidney Disease Dataset](https://www.kaggle.com/datasets/mansoordaku/ckdisease)
- **Key Features**: `age`, `bp`, `bgr`, `bu`, `sc`, `sod`, `pot`, `hemo`, `pcv`, `wc`, `rc`, `htn`, `dm`, `cad`, `appet`, `pe`, `ane`, `classification`

---

### 4. Health Markers Dataset
- **Target File**: `data/raw/health_markers_dataset.csv`
- **Source**: Aggregated and standardized clinical laboratory biomarkers from public CDC NHANES epidemiological cohorts and physiological reference ranges.
- **Key Features**: `glucose`, `hba1c`, `trestbps`, `bloodpressure`, `ldl`, `hdl`, `triglycerides`, `diagnosis`

---

## Preprocessing & Training Pipeline

Once the raw CSV files are placed in `data/raw/`, run the automated preprocessing and training pipeline to generate the processed datasets and model binaries:

```bash
# 1. Clean, impute, and engineer features
python ml_pipeline/preprocessing/preprocess.py

# 2. Train stacking ensemble models & generate evaluation metrics
python ml_pipeline/training/train_models.py

# 3. (Optional) Run hyperparameter tuning with cross-validation
python ml_pipeline/training/hyperparameter_tuning.py
```
