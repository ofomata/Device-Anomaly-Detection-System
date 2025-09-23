# Device Anomaly Detection System

A **serverless web application** to monitor printer anomalies in real-time. It tracks printer metrics like temperature and workload, logs out-of-bound events, and visualizes them for the operations team. The system integrates multiple AWS services with a React frontend, complete with CI/CD deployment.

---

## Architecture Diagram

![Architecture Diagram](./screenshots/architecture.png)

---

## Features

- **AWS IoT Core:** Collects device metrics and triggers Lambda for anomaly detection.  
- **AWS Lambda:** Processes IoT messages, stores data in DynamoDB, and triggers notifications.  
- **DynamoDB:** Stores printer profiles and event logs.  
- **SNS:** Sends notifications for critical anomalies to the operations team.  
- **API Gateway:** Exposes REST endpoints to serve frontend data.  
- **React Frontend:** Displays printer details, events, and visualizations.  
- **CI/CD:** Automates frontend deployment to S3 using GitHub Actions.  

---

## Tech Stack

- **AWS Services:** IoT Core, Lambda, DynamoDB, SNS, API Gateway, CloudWatch, S3, IAM, CI/CD  
- **Frontend:** React  
- **Tools:** AWS CLI, Git, GitHub, cURL  

---

## Project Structure


Device Anomaly Detection System/
│
├── README.md                  # Project documentation
├── backend/                   # AWS backend resources
│   ├── anom_det_policy.json   # IAM policy for Lambda
│   ├── anomaly_rule.json      # IoT Topic Rule
│   ├── iot_lambda_role/       # Lambda IAM role setup
│   ├── printer_iot_data.json  # Test data
│   ├── lambda_function.py     # Main Lambda function
│   ├── api_lambda.py          # API Lambda function
│   └── emit_json_data.py      # Test script for IoT data
│
├── frontend/
│   └── printer-dashboard/     # React application
│
├── screenshots/               # Documentation assets
│   ├── architecture.png
│   ├── frontend-page.png
│   ├── cloudwatch.jpeg
│   ├── iot.jpeg
│   ├── sns.jpeg
│   └── workflow.png

---

## Setup Instructions

1. Create dynamoDB table, Insert table items for number of printer eg Printer 1, Printer 2 etc.
2. Create Lambda function: to process incoming data obtained by IoT Core, check for anomaly, update table and SNS.
3. Create policy to give lambda needed permission to access dynamoDb, IoT, SNS and CloudWatch: create role and attach policy to role.
4. Create IoT topic rule
5. Set up SNS to recieve notification of device anomaly.
Note: only used for testing purpose.
6. Subscribe topic anom/detect in IoT core and run python3 emit_json_data.py anom/detect printer_iot_data.json to test. ensure the data in IoT core, DynamoDB data and SNS notification for anomaly.
7. Set up the React Application for frontend: Clone the frontend repo, install Node.js(if not already installed).
8. Create API Gateway Endpoint; HTTP API, enable GET method with /printers resource. Enable CORS configuration.
9. Create Lambda Function to fetch dynamoDB; connect API Gateway to lambda. update react application with your actual API endpoint.
10. Test the frontend app: Install dependencies and start deployment server.

    npm install
    npm start

11. Create an S3 bucket: enable public access; for testing purpose only, ensure permissions are securely configured in production. Enable Static Website Hosting.
12. Set Up GitHub Repo for Dashboard: 
- create a new repo on github
- push the frontend code for the dashboard to the repo
- create a branch for deploment
13. Automate Deployment with GitHub Action
- in the deploy branch, create .github/workflows/branch-name.yml

```yaml
name: Deploy to S3

on:
  push:
    branches:
      - deploy

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Build React app
        run: npm run build

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v3
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Sync files to S3
        run: aws s3 sync build/ s3://YOUR-BUCKET-NAME --delete
  ```

- define the workflow to configure the CI/CD pipeline
- in the github repo settings, add the following secretes: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
14. Monitor the deployment progress and Verify the deployed application. Access the static website endpoint to ensure the latest version of the dashbaord is deployed

---
