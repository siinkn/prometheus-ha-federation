# 🚀 Prometheus HA Federation Stack

A production-grade, high-availability observability stack using **Prometheus Federation**, **HAProxy**, **Grafana**, **Jaeger**, **OpenTelemetry**, and **Ansible** — designed for **resilience**, **traceability**, and **operational visibility**.

This project deploys seamlessly across multiple VMs using Docker Compose, fully automated by Ansible.

---

## 📐 Architecture Diagram (Updated & Labeled)

```
                   ┌────────────┐
                   │  Grafana   │
                   └────┬───────┘
                        │
              ┌─────────▼──────────┐
              │ HAProxy (LB #1)    │
              │ Grafana → Federation
              └─────────┬──────────┘
                        │
      ┌─────────────────▼─────────────────┐
      │      Prometheus Federation        │
      │          (Central Node)           │
      └────────┬──────────────┬───────────┘
               │              │
     ┌─────────▼────┐   ┌─────▼────────────┐
     │ HAProxy (LB #2)                     │
     │ Federation → Replicas               │
     └────────┬────────────────────────────│
              │               │
              │               │
    ┌─────────▼────┐   ┌──────▼─────────┐
    │ Prometheus 1 │   │ Prometheus 2   │
    └─────┬────────┘   └─────┬──────────┘
          ▼                  ▼
   ┌────────────┐      ┌────────────┐
   │ Node Export│      │ Node Export│
   │    (129)   │      │    (130)   │
   └────────────┘      └────────────┘

             ▲
             │
   ┌─────────┴─────────────┐
   │ Python App (Flask)    │
   │ /metrics + OTEL       │
   └─────────┬─────────────┘
             │
             ▼
         ┌────────┐
         │ Jaeger │
         └────────┘
```

---

## 🔧 Stack Components

### ✅ Metrics
- `node_exporter`: system-level metrics from all nodes
- `prometheus (2x)`: HA scraping from exporters + app
- `prometheus_federation`: centralized metrics aggregation
- `haproxy_exporter`: exposes internal HAProxy stats

### ✅ Tracing
- `python_app (Flask)`: serves Prometheus metrics + sends OTEL spans
- `jaeger`: collects, stores, and visualizes traces

### ✅ Load Balancing
- **HAProxy #1**: exposes a **stable endpoint** to Grafana for accessing the Federation node.  
  📌 If Federation is restarted or relocated, Grafana remains unaffected.
- **HAProxy #2**: enables **load-balanced and fault-tolerant access** from Federation → Prometheus replicas.  
  📌 If one replica goes down, Federation still receives metrics without interruption.

---

## 🚀 Deployment Guide

### 🛠️ Prerequisites

- Ansible installed on control machine
- Docker & Docker Compose on all target nodes
- SSH access configured in `hosts.ini`

### 📂 Deploy in 3 Steps

```bash
# 1. Clone the repo
git clone https://github.com/siinkn/prometheus-ha-federation.git
cd prometheus-ha-federation

# 2. Edit inventory
nano inventories/dev/hosts.ini

# 3. Run full deployment
ansible-playbook -i inventories/dev/hosts.ini playbook.yml
```

> You can run only HAProxy (replica LB) with:
> `--tags replica_haproxy`

---

## 📊 Grafana Dashboard

- Access: `http://<grafana-ip>:3000`
- Login: `admin / admin`
- Prometheus source: `http://<haproxy-ip>:9091`

### Recommended Panels

| Panel | PromQL |
|-------|--------|
| App Latency (p95) | `histogram_quantile(0.95, rate(python_app_request_latency_seconds_bucket[1m]))` |
| Request Rate | `rate(python_app_requests_total[1m])` |
| Backend Sessions | `haproxy_backend_sessions_total{backend="prometheus_backends"}` |
| Replica Health | `haproxy_server_up{backend="prometheus_backends"}` |
| Load Distribution | `rate(haproxy_server_sessions_total[5m]) by (server)` |

---

## 🔭 Jaeger UI

- Access: `http://<jaeger-ip>:16686`
- Service: `python-metrics-app`
- Features: span search, latency graph, trace pathing, service map

---

## ✅ Why This Architecture?

This setup uses **two layers of HAProxy** for maximum resilience:

- 🔁 **HAProxy #1 (Grafana ↔ Federation)**:  
  Decouples Grafana from direct dependency on Federation node.  
  Keeps dashboards online even if the Federation container restarts.

- 🔁 **HAProxy #2 (Federation ↔ Replicas)**:  
  Ensures Prometheus Federation can always fetch metrics, even if one replica fails.  
  Load balancing helps evenly distribute read traffic, preventing overload.

This design achieves:

- True **HA with decoupling** between all components
- **Seamless recovery** from replica/node failure
- **Unified access points** for external tools (Grafana, alerting systems)
- **Operational clarity** via exporters and metrics from both HAProxy layers

---

## 🧩 Extending This Stack

Plug in additional observability tools:

- **Alertmanager** → alert routing via email, Slack, Opsgenie
- **Loki + Promtail** → for logs with Grafana integration
- **Tempo** → OTEL-native distributed tracing
- **Kubernetes targets** → via `kubernetes_sd_config`
- **SLO monitoring** → using `prometheus-mixin` or `nobl9`

---

## ✅ SRE Readiness Checklist

- [x] Prometheus replicas run independently
- [x] Federation node aggregates via HAProxy LB
- [x] Grafana accesses federation via stable HAProxy endpoint
- [x] HAProxy #2 load balances Federation → Replicas
- [x] Flask app exposes metrics + sends OTEL traces
- [x] Jaeger receives + visualizes spans
- [x] All exporters version-pinned (no `latest`)
- [x] HAProxy metrics endpoint is authenticated
- [x] Docker Compose setup is idempotent
- [x] Infrastructure is fully automated via Ansible

---

## 🪪 License

MIT — use freely, adapt for your needs. Attribution appreciated.  
Created by [@siinkn](https://github.com/siinkn)

