# 🤖 K8s AI-Powered Incident Responder

## 📖 Overview
The **K8s AI-Powered Incident Responder** is a proactive, cluster-native DevOps agent designed to dramatically reduce Mean Time To Resolution (MTTR). It continuously monitors Kubernetes clusters for failing Pods (e.g., `CrashLoopBackOff`, `Error`), automatically extracts their recent logs, and leverages **Google's Gemini 2.5 Flash AI** to perform an instant Root Cause Analysis (RCA). The actionable insights are then instantly routed to a configured **Slack** channel.

[Image of Kubernetes architecture diagram showing a custom AI agent pod communicating with K8s API, a Redis cache, Gemini API, and a Slack webhook]

## ✨ Key Features
* **Real-time Monitoring:** Actively watches Kubernetes Event streams for pod failures across all namespaces using native K8s RBAC.
* **AI-Driven RCA:** Integrates with the Google GenAI SDK to translate cryptic stack traces and K8s errors into human-readable root cause analyses and actionable remediation steps.
* **Smart Deduplication:** Utilizes **Redis** to cache failure events, preventing alert fatigue and spamming in your Slack channels when pods enter a continuous crash loop.
* **Instant Alerting:** Pushes perfectly formatted, context-rich alerts directly to Slack via Incoming Webhooks.
* **Production-Ready Packaging:** Fully packaged as a **Helm Chart**, ensuring declarative installation, easy configuration, and secure secret injection.

## 🏗️ Architecture
1. **Agent Pod:** A Python-based agent utilizing the `kubernetes-client` to watch for `Warning` events.
2. **State Store:** A Redis instance used to track processed events with a TTL (Time-To-Live) mechanism.
3. **AI Engine:** Google Gemini AI processes the failure context (Reason, Message, and last 50 lines of logs).
4. **Alerting Pipeline:** HTTP POST requests deliver the final payload to Slack.

## 📋 Prerequisites
* A running Kubernetes Cluster (Minikube, Kind, EKS, GKE, etc.)
* `kubectl` and `helm` installed locally.
* A Gemini API Key (from Google AI Studio).
* A Slack Incoming Webhook URL.

## 🚀 Installation