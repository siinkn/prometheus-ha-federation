# 🚀 Prometheus HA Federation Stack

A production-grade, high-availability observability stack using [Prometheus Federation](https://prometheus.io/docs/prometheus/latest/federation/), [HAProxy](http://www.haproxy.org/), [Grafana](https://grafana.com/), [Jaeger](https://www.jaegertracing.io/), [OpenTelemetry](https://opentelemetry.io/), and [Ansible](https://www.ansible.com/) — designed for **resilience**, **traceability**, and **full-stack observability**.

This project is deployed across multiple VMs using Docker Compose, fully automated with Ansible.

---

## 📐 Architecture Diagram

```
                   ┌────────────┐
                   │  Grafana   │
                   └────┬───────┘
                        │
              ┌─────────▼─────────────┐
              │ HAProxy (LB #1)       │
              │ Grafana → Federation  │
              └─────────┬─────────────┘
                        │
        ┌───────────────▼────────────────┐
        │     Prometheus Federation      │
        │         (Central Node)         │
        └─────────┬────────────┬─────────┘
                  │            │
        ┌─────────▼────┐ ┌─────▼─────────┐
        │ HAProxy (LB #2)         │
        │ Federation → Replicas   │
        └────────┬────────────────┘
                 │
        ┌────────▼────┐   ┌──────▼─────────┐
        │ Prometheus1 │   │ Prometheus2    │
        └─────┬────────┘   └─────┬──────────┘
              ▼                  ▼
        ┌────────────┐     ┌────────────┐
        │ NodeExporter│     │ NodeExporter│
        │    (129)    │     │    (130)    │
        └────────────┘     └────────────┘

                ▲
                │
     ┌──────────┴────────────┐
     │ Python App (Flask)    │
     │ /metrics + OTEL       │
     └──────────┬────────────┘
                │
                ▼
            ┌────────┐
            │ Jaeger │
            └────────┘
```

---

## 🔧 Stack Components

### ✅ Metrics
- `node_exporter`: system-level metrics from each node
- `prometheus` (2x): HA replicas scraping metrics
- `prometheus_federation`: centralized aggregation node
- `haproxy_exporter`: exposes HAProxy metrics

### ✅ Tracing
- `python_app (Flask)`: exposes `/metrics` and sends OpenTelemetry spans
- `jaeger`: collects, stores, and visualizes traces

### ✅ Load Balancing

#### 🔁 HAProxy #1 – Grafana → Federation
- Exposes a **stable endpoint** to Grafana, even if Federation restarts or relocates.
- Prevents downtime in dashboards due to federation issues.

#### 🔁 HAProxy #2 – Federation → Replicas
- Enables **load-balanced and fault-tolerant access** from Federation to Prometheus replicas.
- Ensures availability even if one replica fails.
- Distributes read traffic evenly.

---

## 🚀 Deployment Guide

### 🛠️ Prerequisites

- [Ansible](https://www.ansible.com/) on the control machine
- Docker & Docker Compose on all target nodes
- SSH access configured in `hosts.ini`

### 🧪 Deploy in 3 Steps

```bash
# 1. Clone the repo
git clone https://github.com/siinkn/prometheus-ha-federation.git
cd prometheus-ha-federation

# 2. Configure inventory
nano inventories/dev/hosts.ini

# 3. Deploy everything
ansible-playbook -i inventories/dev/hosts.ini playbook.yml
```

> Optional: Deploy only HAProxy (Replica LB)  
> `ansible-playbook ... --tags replica_haproxy`

---

## 📊 Grafana

- **URL**: `http://<grafana-ip>:3000`
- **Login**: `admin / admin`
- **Data Source**: `http://<haproxy-ip>:9091`

### 🔍 Recommended Panels

| Panel | PromQL |
|-------|--------|
| **App Latency (p95)** | `histogram_quantile(0.95, rate(python_app_request_latency_seconds_bucket[1m]))` |
| **Request Rate** | `rate(python_app_requests_total[1m])` |
| **Backend Sessions** | `haproxy_backend_sessions_total{backend="prometheus_backends"}` |
| **Replica Health** | `haproxy_server_up{backend="prometheus_backends"}` |
| **Load Distribution** | `rate(haproxy_server_sessions_total[5m]) by (server)` |

---

## 🔭 Jaeger

- **UI**: `http://<jaeger-ip>:16686`
- **Service**: `python-metrics-app`
- **Features**: span search, service map, trace flow, latency breakdown

---

## 🤔 Why This Architecture?

This stack uses **two layers of HAProxy** for precise control, stability, and fault tolerance:

### 🔁 HAProxy #1 – Grafana ↔ Federation
- Abstracts Grafana away from direct contact with the Federation node.
- Keeps dashboards live even during container restarts or redeployments.

### 🔁 HAProxy #2 – Federation ↔ Replicas
- Adds a high-availability layer for scraping from multiple replicas.
- Ensures the Federation node always has access to data.
- Simplifies backend switching or replica scaling.

**This architecture delivers:**
- 🔒 Reliable external access via stable HAProxy frontends
- 🔄 Continuous Federation-level metric access
- 🧠 Modular, extensible structure with minimal SPOFs
- 📈 Clear observability for all HAProxy layers through exporters

---

## 🧩 Extending This Stack

| Tool | Purpose |
|------|---------|
| [Alertmanager](https://prometheus.io/docs/alerting/latest/alertmanager/) | Alert routing (email, Slack, Opsgenie) |
| [Loki + Promtail](https://grafana.com/oss/loki/) | Log aggregation with Grafana |
| [Tempo](https://grafana.com/oss/tempo/) | OTEL-native distributed tracing |
| Kubernetes SD | Add Kubernetes scrape configs for cluster metrics |
| SLO Dashboards | Integrate `prometheus-mixin` or tools like `nobl9` |

---

## ✅ SRE Readiness Checklist

- [x] Prometheus replicas scrape independently
- [x] Federation aggregates via HAProxy LB
- [x] Grafana connects via HAProxy #1 (stable access)
- [x] Federation connects to replicas via HAProxy #2
- [x] Flask app emits metrics + traces
- [x] Jaeger visualizes OTEL spans
- [x] Exporters version-pinned
- [x] HAProxy stats protected with auth
- [x] Infrastructure fully automated via Ansible

---

## 🪪 License

MIT — use freely, adapt for your needs. Attribution appreciated.  
Created by [@siinkn](https://github.com/siinkn)

