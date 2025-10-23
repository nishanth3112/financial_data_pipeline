# Real-Time Financial Data Pipeline

![Python](https://img.shields.io/badge/Python-3.10-blue)
![PySpark](https://img.shields.io/badge/Framework-PySpark-orange)
![Docker](https://img.shields.io/badge/Container-Docker-2496ED)
![AWS](https://img.shields.io/badge/Cloud-AWS-FF9900)
![S3](https://img.shields.io/badge/Service-AWS%20S3-yellow)
![EC2](https://img.shields.io/badge/Service-AWS%20EC2-lightgrey)
![EMR](https://img.shields.io/badge/Service-AWS%20EMR-green)
![Glue](https://img.shields.io/badge/Service-AWS%20Glue-8C4FFF)
![Athena](https://img.shields.io/badge/Service-AWS%20Athena-232F3E)
![SQL](https://img.shields.io/badge/Language-SQL-blueviolet)
![API](https://img.shields.io/badge/API-OpenExchangeRates-lightblue)
![ETL](https://img.shields.io/badge/Process-ETL%20Pipeline-brightgreen)

### 📌 Overview
This project automates the normalization of raw **bank transaction data** into a single base currency (SGD) using **AWS Cloud Services** and **PySpark**.  
It integrates **real-time exchange rate APIs** with transactional data to produce standardized, analytics-ready outputs in **S3**, enabling business teams to make accurate credit and lending decisions.

---

## 🚀 Business Context
Financial institutions deal with deposits and withdrawals in multiple currencies (INR, USD, SGD, etc.).  
For consistent analysis—especially for **credit evaluation, remittance, and cross-border transactions**—data must be normalized to a single base currency.  
This project creates an **end-to-end cloud pipeline** that:
- Fetches real-time **exchange rates** using an API in Docker on **AWS EC2**
- Transforms and normalizes data using **PySpark on AWS EMR**
- Stores curated results in **AWS S3** as **partitioned Parquet files**
- Catalogs data with **AWS Glue**
- Enables **SQL analysis in Athena**

---

## 🧱 Architecture

---

## ⚙️ Tech Stack

| Category | Technologies |
|-----------|--------------|
| **Programming** | Python, SQL |
| **Framework** | PySpark |
| **Containerization** | Docker |
| **Cloud Services** | AWS EC2, S3, EMR, Glue, Athena |
| **API Source** | [Open Exchange Rates](https://openexchangerates.org/signup/free) |

---

## 🪶 Data Description

**1️⃣ Bank Transaction Data**
| Column | Description |
|---------|-------------|
| Account_ID | Unique ID for bank account |
| Date | Date of transaction |
| Transaction_details | Description of transaction |
| Chq_no | Cheque number (optional) |
| Value_date | Date of value |
| Withdrawal_amt | Amount withdrawn |
| Withdrawal_currency | Currency of withdrawal |
| Deposit_amt | Amount deposited |
| Deposit_currency | Currency of deposit |
| Balance_amt | Post-transaction balance |

**2️⃣ API Data**
Fetched from [Open Exchange Rates](https://openexchangerates.org/signup/free), containing:
- `timestamp`
- `base` currency
- `rates` dictionary (mapping currency → exchange rate)

---

## 🧩 Workflow Steps

### **Step 1 — Data Ingestion**
- Create an S3 bucket for raw and processed data.
- Upload raw transaction CSV file into the bucket.
- Launch an EC2 instance and install Docker.

### **Step 2 — API Extraction**
- Inside Docker, use Python script to call Open Exchange API:
  ```bash
  python main.py --run_ts "2025-01-01"   --config '{"app_id":"<your_app_id>", "s3_out_location":"s3://your-bucket/api_response/", "s3_error_out_location":"s3://your-bucket/error/"}'
  ```

---

### **Step 3 — Spark Normalization**

Launch an EMR cluster.

SSH into the EMR master node:
```bash
ssh -i <your-key.pem> hadoop@<emr-master-public-dns>
```

Run the Spark job:
```bash
spark-submit s3://your-bucket/code/transform.py
```

---

### **Step 4 — Glue Catalog & Athena**

- Create AWS Glue Crawler on the processed S3 folder.  
- Run crawler → generates Glue Catalog.  
- Query normalized data in Athena using SQL.

---

## 🐳 Docker Setup (EC2)

```bash
# Update packages
sudo yum update -y

# Install Docker
sudo yum install docker -y
sudo service docker start

# Add EC2 user to Docker group
sudo usermod -a -G docker ec2-user
# Re-login after this step
```

---

### **Docker Commands**

```bash
# Build Docker image
docker build -t mudra . -f Dockerfile

# Run container
docker run -dit mudra

# Access container shell
docker exec -it <container_id> /bin/bash

# Copy AWS credentials into container
docker cp /home/ec2-user/aws.txt <container_id>:/root/
mv /root/aws.txt /root/.aws/credentials
chmod 600 /root/.aws/credentials
```

---

## 📊 Athena Query Example

```sql
SELECT
  Account_ID,
  Date,
  ROUND(Deposit_amt_SGD, 2) AS Deposit_SGD,
  ROUND(Withdrawal_amt_SGD, 2) AS Withdrawal_SGD,
  Balance_amt_SGD
FROM normalized_transactions
WHERE Date BETWEEN '2024-01-01' AND '2024-12-31'
ORDER BY Date ASC;
```

---

## 🧠 Key Learnings

✅ Building a real-world AWS data pipeline (S3, EC2, EMR, Glue, Athena)  
✅ Containerizing API ingestion using Docker on EC2  
✅ Implementing PySpark transformations for currency normalization  
✅ Automating ETL & data cataloging with AWS Glue  
✅ Querying large datasets serverlessly using Athena  

---

## ⚠️ Notes

💡 Always terminate EC2, EMR clusters, and Glue jobs after use to prevent unnecessary AWS billing.  
💾 Use versioned S3 buckets for audit tracking.  
🔐 Store sensitive credentials (e.g., OpenExchange API key) in `.env` or AWS Secrets Manager.  

---

## 📈 Future Enhancements

- Integrate Airflow or Step Functions for orchestration.  
- Use AWS Lambda to automate API ingestion on schedule.  
- Add visualization layer using Amazon QuickSight or Tableau.  
- Enable CI/CD using GitHub Actions for Docker + EMR deployment.  

---
