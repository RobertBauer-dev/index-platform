# Index Platform Monitoring

> **Umfassendes Monitoring-Setup mit Prometheus und Grafana**  
> Enterprise-grade Überwachung für alle Komponenten der Index Platform

## 📋 Übersicht

Das Monitoring-Setup umfasst:

- **Prometheus**: Metriken-Sammlung und -Speicherung
- **Grafana**: Visualisierung und Dashboards
- **Alertmanager**: Alerting und Benachrichtigungen
- **Exporters**: Spezialisierte Metriken-Exporter für verschiedene Services
- **Custom Metrics**: Business-spezifische Metriken für die Index Platform

## 🏗️ Architektur

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Applications  │    │   Exporters     │    │   Prometheus    │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Backend API │ │◄──►│ │ Node Export │ │◄──►│ │ Time Series │ │
│ │ Frontend    │ │    │ │ cAdvisor    │ │    │ │ Database    │ │
│ │ Database    │ │    │ │ Postgres    │ │    │ │ Rules       │ │
│ │ Redis       │ │    │ │ Redis       │ │    │ │ Alerting    │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Grafana       │    │ Alertmanager    │    │   Notifications │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Dashboards  │ │    │ │ Alert Rules │ │    │ │ Email       │ │
│ │ Visualiz.   │ │    │ │ Routing     │ │    │ │ Slack       │ │
│ │ Alerts      │ │    │ │ Inhibition  │ │    │ │ Webhooks    │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Schnellstart

### Mit Docker Compose

```bash
# Monitoring-Services starten
docker-compose up -d prometheus grafana alertmanager

# Setup-Script ausführen
./scripts/setup-monitoring.sh
```

### Mit Kubernetes

```bash
# Monitoring-Namespace erstellen
kubectl create namespace monitoring

# Prometheus deployen
kubectl apply -f k8s/monitoring/prometheus.yaml

# Grafana deployen
kubectl apply -f k8s/monitoring/grafana.yaml

# Exporters deployen
kubectl apply -f k8s/monitoring/exporters.yaml
```

## 📊 Verfügbare Dashboards

### 1. Backend API Dashboard
- **Request Rate**: HTTP-Anfragen pro Sekunde
- **Response Time**: 50th, 95th, 99th Percentile
- **Error Rate**: 4xx und 5xx Fehler
- **Active Connections**: Aktive Verbindungen
- **Memory/CPU Usage**: Ressourcenverbrauch
- **Database Connections**: DB-Verbindungen
- **Redis Memory**: Cache-Speicher

### 2. Infrastructure Dashboard
- **Node CPU/Memory**: Server-Ressourcen
- **Container Metrics**: Container-Performance
- **Disk Usage**: Speicherplatz
- **Network Traffic**: Netzwerk-Traffic
- **Pod Status**: Kubernetes Pod-Status
- **Service Health**: Service-Gesundheit

### 3. Business Metrics Dashboard
- **Index Calculations**: Berechnungen pro Stunde
- **Data Ingestion Rate**: Datenaufnahme-Rate
- **Active Users**: Aktive Benutzer
- **Total Securities/Indices**: Gesamtanzahl
- **API Requests Today**: Tägliche API-Aufrufe
- **Performance Distribution**: Performance-Verteilung
- **Data Quality Score**: Datenqualitäts-Score

## 🔔 Alerting-Regeln

### Kritische Alerts (Critical)
- **High Error Rate**: >10% Fehlerrate für 2 Minuten
- **Database Connection Failure**: DB nicht erreichbar
- **Redis Connection Failure**: Redis nicht erreichbar
- **Index Calculation Failure**: Index-Berechnung fehlgeschlagen
- **Low Disk Space**: <10% freier Speicherplatz
- **Service Down**: Service nicht erreichbar

### Warnungen (Warning)
- **High Response Time**: >2s Response-Zeit für 5 Minuten
- **High Memory Usage**: >1GB Speicherverbrauch
- **High CPU Usage**: >80% CPU für 5 Minuten
- **Data Ingestion Failures**: >5 Fehler in 5 Minuten
- **High Container Memory**: >90% Container-Speicher
- **Pod Restart**: Pod-Neustarts

## 📈 Custom Metrics

### Backend API Metriken
```python
# HTTP-Anfragen
http_requests_total{method, endpoint, status}

# Response-Zeit
http_request_duration_seconds{method, endpoint}

# Aktive Verbindungen
http_connections_active
```

### Business Metriken
```python
# Index-Berechnungen
index_calculations_total{index_id, method}
index_calculation_duration_seconds{index_id, method}
index_calculation_errors_total{index_id, error_type}

# Datenaufnahme
data_ingestion_records_total{source, type}
data_ingestion_errors_total{source, error_type}
data_quality_score{data_type}

# System-Metriken
active_users_total
securities_total
indices_total
```

### Datenbank-Metriken
```python
# DB-Verbindungen
db_connections_active
db_query_duration_seconds{query_type}

# Cache-Metriken
cache_hits_total{cache_type}
cache_misses_total{cache_type}
cache_size_bytes{cache_type}
```

## 🛠️ Konfiguration

### Prometheus-Konfiguration
```yaml
# monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'backend-api'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
```

### Grafana-Datasource
```yaml
# monitoring/grafana/provisioning/datasources/prometheus.yml
datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    isDefault: true
```

### Alertmanager-Konfiguration
```yaml
# monitoring/alertmanager/alertmanager.yml
route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
  - name: 'critical-alerts'
    email_configs:
      - to: 'admin@indexplatform.com'
```

## 🔧 Wartung und Troubleshooting

### Service-Status prüfen
```bash
# Docker Compose
docker-compose ps
docker-compose logs prometheus
docker-compose logs grafana

# Kubernetes
kubectl get pods -n index-platform
kubectl logs -f deployment/prometheus -n index-platform
```

### Metriken-Endpoint testen
```bash
# Backend-Metriken
curl http://localhost:8000/metrics

# Prometheus-Targets
curl http://localhost:9090/api/v1/targets
```

### Grafana-Dashboards importieren
1. Grafana öffnen: http://localhost:3001
2. Login: admin/admin
3. Dashboards automatisch verfügbar durch Provisioning

### Alerting testen
```bash
# Test-Alert senden
curl -X POST http://localhost:9093/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '[{
    "labels": {
      "alertname": "TestAlert",
      "severity": "warning"
    },
    "annotations": {
      "summary": "Test alert",
      "description": "This is a test alert"
    }
  }]'
```

## 📚 Erweiterte Konfiguration

### Custom Dashboards erstellen
1. Grafana-Dashboard erstellen
2. JSON exportieren
3. In `monitoring/grafana/dashboards/` speichern
4. Automatisch durch Provisioning geladen

### Neue Metriken hinzufügen
```python
# In backend/app/core/metrics.py
new_metric = Counter(
    'new_metric_total',
    'Description of new metric',
    ['label1', 'label2']
)

# Metriken verwenden
new_metric.labels(label1='value1', label2='value2').inc()
```

### Alerting-Regeln erweitern
```yaml
# In monitoring/prometheus/rules/
groups:
  - name: custom.rules
    rules:
      - alert: CustomAlert
        expr: custom_metric > threshold
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Custom alert triggered"
```

## 🔐 Sicherheit

### Zugriffskontrolle
- Grafana: Admin-Passwort in Umgebungsvariablen
- Prometheus: Keine Authentifizierung (internes Netzwerk)
- Alertmanager: Webhook-Authentifizierung

### Netzwerk-Sicherheit
- Monitoring-Services nur im internen Netzwerk
- Externe Zugriffe über Reverse Proxy
- TLS-Verschlüsselung für externe Kommunikation

## 📞 Support

Bei Problemen mit dem Monitoring:

1. **Logs prüfen**: `docker-compose logs [service]`
2. **Service-Status**: `docker-compose ps`
3. **Metriken-Endpoint**: `curl http://localhost:8000/metrics`
4. **Prometheus-Targets**: http://localhost:9090/targets
5. **Grafana-Health**: http://localhost:3001/api/health

---

**Monitoring-Setup für Enterprise-Grade Überwachung der Index Platform**
