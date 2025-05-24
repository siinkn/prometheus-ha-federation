# 🚀 Prometheus HA Monitoring Stack

A high-availability observability stack using **Prometheus**, **HAProxy**, **Grafana**, **Jaeger**, **OpenTelemetry**, and **Ansible** — built for redundancy, traceability, and full-stack insight.

This system is deployed across multiple virtual machines using Docker Compose and automated with Ansible.

---

## 📌 Architecture Overview

```
                ┌────────────┐
                │  Grafana   │
                │(dashboards)│
                └────┬───────┘
                     │
           ┌─────────▼─────────┐
           │   HAProxy (LB)    │
           │ (for Grafana only)│
           └────────┬──────────┘
                    │
     ┌──────────────▼──────────────┐
     │ Prometheus Federation Node  │
     │         (node131)           │
     └─────┬──────────┬────────────┘
           │          │
┌──────────▼───┐  ┌───▼────────────┐
│ Prometheus   │  │  Prometheus    │
│  Replica 1   │  │   Replica 2    │
│  (node129)   │  │   (node130)    │
└──────┬───────┘  └─────┬──────────┘
       │                │
       ▼                ▼
┌────────────┐     ┌────────────┐
│ Node Exporter│   │ Node Exporter│
│ (129)       │   │ (130)       │
└────────────┘     └────────────┘

      ▲
      │
┌─────┴────────────────────┐
│     Python App (Flask)   │
│  - /metrics → Prometheus │
│  - OTEL → Jaeger         │
└──────────┬───────────────┘
           │
           ▼
      ┌─────────────┐
      │   Jaeger    │
      │ (Trace UI)  │
      └─────────────┘
```

---

## 🔧 Components

### ✅ Metrics

- **node_exporter**: system-level metrics
- **prometheus** (x2): scrapes node_exporter, app, and exporters
- **prometheus_federation**: scrapes both replicas centrally
- **haproxy_exporter**: exposes HAProxy stats to Prometheus

### ✅ Tracing

- **python_app (Flask)**: exposes `/metrics` and sends OpenTelemetry traces
- **jaeger**: receives spans and provides UI

---

## 🚀 Deployment Guide

### 📌 Prerequisites

- Ansible on the control machine
- Docker & Docker Compose on all target nodes
- SSH access (configured in `hosts.ini`)

---

### 📂 Step-by-Step

```bash
# 1. Clone the repo
git clone https://github.com/siinkn/prometheus-ha.git
cd prometheus-ha

# 2. Edit inventory
nano inventories/dev/hosts.ini
# Add your VM IPs and groups

# 3. Run Ansible
ansible-playbook -i inventories/dev/hosts.ini playbook.yml
```

This will:
- Generate config files
- Deploy all containers with Docker Compose
- Setup networking and exporters automatically

---

## 📊 Grafana Setup

- Access: `http://<grafana-ip>:3000`
- Login: `admin / admin`
- Add Prometheus data source pointing to: `http://<haproxy-ip>:9091`
- Optional: Import common dashboards manually (Node Exporter, HAProxy, etc.)

---

## 🔭 Jaeger Tracing

- Access: `http://<jaeger-ip>:16686`
- App spans appear under `python-metrics-app`
- Real-time latency, path tracing, service map available

---

## 📈 Suggested Grafana Panels

| Panel Title               | PromQL                                                                 |
|--------------------------|-------------------------------------------------------------------------|
| App Latency (p95)        | `histogram_quantile(0.95, rate(python_app_request_latency_seconds_bucket[1m]))` |
| App Request Rate         | `rate(python_app_requests_total[1m])`                                   |
| Backend Sessions         | `haproxy_backend_sessions_total{backend="prometheus_backends"}`         |
| Prometheus Targets Down  | `up{job="prometheus"} == 0`                                              |
| HAProxy Server Health    | `haproxy_server_up{backend="prometheus_backends"}`                      |
| Load Distribution        | `rate(haproxy_server_sessions_total[5m]) by (server)`                   |

---

## ✅ SRE Readiness Checklist

- [x] Prometheus replicas scrape exporters independently
- [x] Federation node aggregates metrics from both replicas
- [x] HAProxy provides a stable endpoint for Grafana
- [x] Python app emits metrics and OpenTelemetry traces
- [x] Jaeger receives traces from app
- [x] Grafana visualizes metrics via HAProxy
- [x] Images are version-pinned (no `latest`)
- [x] HAProxy metrics endpoint secured with auth
- [x] Ansible fully automates setup

---

## 🪪 License

MIT — Free to use, modify, and distribute. Attribution appreciated.


