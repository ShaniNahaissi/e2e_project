# Kubernetes AI Incident Responder

## Overview
The Kubernetes AI Incident Responder is a tool that helps you fix failing pods faster. It automatically watches your Kubernetes cluster for errors. When a pod crashes, it grabs the error logs, asks Google's Gemini AI to explain why it crashed, and sends a simple, clear solution to your Slack channel.



## Key Features
* **Automated Monitoring:** Constantly watches for pod failures across your cluster.
* **AI Analysis:** Uses Gemini AI to translate confusing Kubernetes errors into plain English.
* **No Alert Spam:** Uses Redis to remember recent alerts, so it won't spam your Slack if a pod keeps crashing in a loop.
* **Slack Integration:** Sends the AI's explanation directly to your team.
* **Easy to Install:** Packaged as a Helm Chart for quick and secure setup.

## How It Works
1. **The Agent:** A Python script watches the Kubernetes API for warning events.
2. **Redis Cache:** Keeps track of recent errors to prevent duplicate alerts.
3. **AI Engine:** Sends the pod's logs to Gemini AI for analysis.
4. **Slack Alert:** Sends the final, easy-to-read report to your Slack workspace.

## Prerequisites
* A running Kubernetes Cluster (Kind, Minikube, EKS, etc.)
* `kubectl` and `helm` installed on your machine.
* A Gemini API Key.
* A Slack Incoming Webhook URL.

## Installation
You can deploy the entire setup using Helm. Your sensitive API keys are passed during installation so they are never saved in your code.

```bash
# 1. Clone the repository
git clone [https://github.com/YOUR_USERNAME/k8s-ai-responder.git](https://github.com/YOUR_USERNAME/k8s-ai-responder.git)
cd k8s-ai-responder

# 2. Deploy Redis 
helm repo add bitnami [https://charts.bitnami.com/bitnami](https://charts.bitnami.com/bitnami)
helm install my-redis bitnami/redis --set architecture=standalone

# 3. Deploy the AI Agent 
helm upgrade --install my-ai-agent ./ai-agent-chart \
  --set secrets.geminiApiKey="YOUR_GEMINI_API_KEY" \
  --set secrets.slackWebhookUrl="YOUR_SLACK_WEBHOOK_URL"