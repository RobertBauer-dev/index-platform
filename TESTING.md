# Index Platform - Testing Guide

> **Umfassende Test-Suite für die Index Platform**  
> Unit-, Integration-, Performance-, System- und E2E-Tests

## 📋 Übersicht

Die Index Platform verfügt über eine vollständige Test-Suite, die alle Aspekte der Anwendung abdeckt:

- **Unit Tests**: Testen einzelner Funktionen und Klassen
- **Integration Tests**: Testen der API-Endpoints und Datenbankintegration
- **Performance Tests**: Load Testing und Performance-Messungen
- **System Tests**: End-to-End Workflow-Tests
- **E2E Tests**: Frontend-Backend Integration Tests

## 🏗️ Test-Architektur

```
tests/
├── backend/
│   ├── unit/                    # Unit Tests
│   │   ├── test_security.py
│   │   ├── test_index_calculation.py
│   │   └── test_data_processing.py
│   ├── integration/             # Integration Tests
│   │   ├── test_api_endpoints.py
│   │   └── test_database_integration.py
│   ├── performance/             # Performance Tests
│   │   ├── test_load_testing.py
│   │   └── locustfile.py
│   └── system/                  # System Tests
│       └── test_end_to_end_workflows.py
└── frontend/
    └── e2e/                     # E2E Tests
        ├── dashboard.spec.ts
        ├── index-builder.spec.ts
        └── authentication.spec.ts
```

## 🚀 Schnellstart

### Alle Tests ausführen
```bash
# Mit dem Test-Script
./scripts/run-tests.sh

# Oder manuell
cd backend && pytest
cd frontend && npm test
```

### Spezifische Test-Typen
```bash
# Unit Tests
./scripts/run-tests.sh --type unit

# Integration Tests
./scripts/run-tests.sh --type integration

# Performance Tests
./scripts/run-tests.sh --type performance

# E2E Tests
./scripts/run-tests.sh --type e2e

# Mit Coverage
./scripts/run-tests.sh --coverage
```

## 🧪 Unit Tests

### Backend Unit Tests
```bash
cd backend
pytest tests/unit/ -v
```

**Abgedeckte Module:**
- Security-Funktionen (Passwort-Hashing, JWT)
- Datenbereinigung und -transformation
- Index-Berechnungslogik
- Datenvalidierung
- Business-Logic

**Beispiel:**
```python
def test_password_hashing():
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)
```

### Frontend Unit Tests
```bash
cd frontend
npm run test:unit
```

**Abgedeckte Komponenten:**
- React-Komponenten
- Utility-Funktionen
- API-Services
- State Management

## 🔗 Integration Tests

### API-Endpoint Tests
```bash
cd backend
pytest tests/integration/test_api_endpoints.py -v
```

**Getestete Endpoints:**
- Authentication (`/api/v1/auth/*`)
- Securities (`/api/v1/securities/*`)
- Indices (`/api/v1/indices/*`)
- Price Data (`/api/v1/securities/*/prices`)
- Data Ingestion (`/api/v1/ingestion/*`)
- GraphQL (`/graphql`)

**Beispiel:**
```python
def test_get_securities(client, auth_headers, test_security):
    response = client.get("/api/v1/securities", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
```

### Datenbank-Integration Tests
```bash
cd backend
pytest tests/integration/test_database_integration.py -v
```

**Getestete Operationen:**
- CRUD-Operationen für alle Modelle
- Datenbankbeziehungen
- Constraints und Validierungen
- Transaktionen

## ⚡ Performance Tests

### Load Testing mit Locust
```bash
cd backend
locust -f tests/performance/locustfile.py --web-host=0.0.0.0
```

**Simulierte Benutzer:**
- **IndexPlatformUser**: Normale API-Nutzung
- **AnonymousUser**: Unauthentifizierte Anfragen
- **DataIngestionUser**: Datenaufnahme-Operationen
- **GraphQLUser**: GraphQL-API-Nutzung

**Performance-Metriken:**
- Response Time (95th Percentile < 2s)
- Throughput (> 100 requests/second)
- Error Rate (< 1%)
- Memory Usage (< 500MB)

### Backend Performance Tests
```bash
cd backend
pytest tests/performance/test_load_testing.py -v
```

**Getestete Szenarien:**
- Einzelne API-Anfragen
- Gleichzeitige Anfragen
- Hohe Last (200+ Requests)
- Große Datensätze (1000+ Records)
- Speicherverbrauch
- CPU-Auslastung

## 🔄 System Tests

### End-to-End Workflows
```bash
cd backend
pytest tests/system/test_end_to_end_workflows.py -v
```

**Getestete Workflows:**
- Komplette Datenaufnahme (CSV → DB → API)
- Index-Erstellung und -Berechnung
- Benutzer-Registrierung und -Authentifizierung
- Datenverarbeitung und -Transformation
- Monitoring und Alerting
- Fehlerbehandlung und -Wiederherstellung

**Beispiel:**
```python
def test_security_ingestion_workflow(client, admin_auth_headers, db_session):
    # 1. CSV erstellen
    csv_content = "symbol,name,exchange,currency,sector,industry,country,market_cap\nAAPL,Apple Inc.,NASDAQ,USD,Technology,Consumer Electronics,USA,3000000000000"
    
    # 2. Über API ingestieren
    files = {"file": ("securities.csv", csv_content, "text/csv")}
    response = client.post("/api/v1/ingestion/csv/securities", files=files, headers=admin_auth_headers)
    
    # 3. In Datenbank verifizieren
    securities = db_session.query(Security).all()
    assert len(securities) >= 1
    
    # 4. Über API abrufen
    response = client.get("/api/v1/securities", headers=admin_auth_headers)
    assert response.status_code == 200
```

## 🎭 E2E Tests

### Frontend E2E Tests mit Playwright
```bash
cd frontend
npx playwright test
```

**Getestete Szenarien:**
- Dashboard-Funktionalität
- Index Builder Workflow
- Authentifizierung
- Responsive Design
- Fehlerbehandlung

**Beispiel:**
```typescript
test('should display dashboard overview', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await page.fill('[data-testid="username-input"]', 'admin');
  await page.fill('[data-testid="password-input"]', 'admin123');
  await page.click('[data-testid="login-button"]');
  
  await page.waitForURL('**/dashboard');
  await expect(page.locator('[data-testid="dashboard-title"]')).toBeVisible();
  await expect(page.locator('[data-testid="total-indices"]')).toBeVisible();
});
```

## 📊 Coverage Reports

### Backend Coverage
```bash
cd backend
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

**Ziel-Coverage:**
- Gesamt: > 80%
- Kritische Module: > 90%
- API-Endpoints: > 95%

### Frontend Coverage
```bash
cd frontend
npm run test:coverage
open coverage/index.html
```

## 🔧 Test-Konfiguration

### Pytest-Konfiguration
```ini
# backend/pytest.ini
[tool:pytest]
testpaths = tests
addopts = 
    -v
    --cov=app
    --cov-report=html
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    system: System tests
```

### Playwright-Konfiguration
```typescript
// frontend/playwright.config.ts
export default defineConfig({
  testDir: './src/tests/e2e',
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
});
```

## 🚀 CI/CD Integration

### GitHub Actions
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
      redis:
        image: redis:7
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: |
          cd backend
          pytest tests/ --cov=app --cov-report=xml
```

**Test-Pipeline:**
1. **Backend Tests**: Unit, Integration, Performance, System
2. **Frontend Tests**: Unit, E2E
3. **Security Tests**: Bandit, Safety
4. **Load Tests**: Locust (nur auf main branch)

## 📈 Test-Metriken

### Performance-Benchmarks
- **API Response Time**: < 2s (95th percentile)
- **Database Queries**: < 500ms
- **Index Calculation**: < 10s
- **Memory Usage**: < 500MB
- **Throughput**: > 100 req/s

### Quality-Metriken
- **Test Coverage**: > 80%
- **Code Quality**: A+ (SonarQube)
- **Security Score**: > 8.0 (Bandit)
- **Dependency Safety**: 0 vulnerabilities

## 🐛 Debugging Tests

### Backend Tests debuggen
```bash
# Mit Debugger
pytest tests/unit/test_security.py::test_password_hashing --pdb

# Mit detailliertem Output
pytest tests/unit/test_security.py -v -s

# Nur fehlgeschlagene Tests
pytest --lf
```

### Frontend Tests debuggen
```bash
# Playwright UI Mode
npx playwright test --ui

# Debug Mode
npx playwright test --debug

# Mit Browser
npx playwright test --headed
```

## 📝 Test-Daten

### Fixtures und Mocks
```python
# backend/tests/conftest.py
@pytest.fixture
def test_user(db_session):
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    return user
```

### Test-Datenbank
- **SQLite**: Für Unit Tests
- **PostgreSQL**: Für Integration Tests
- **In-Memory**: Für Performance Tests

## 🔍 Test-Reporting

### HTML Reports
- **Backend**: `backend/htmlcov/index.html`
- **Frontend**: `frontend/coverage/index.html`
- **E2E**: `frontend/playwright-report/index.html`
- **Load Tests**: `backend/load-test-report.html`

### CI/CD Reports
- **Test Results**: JUnit XML
- **Coverage**: Codecov Integration
- **Security**: Security Reports
- **Performance**: Load Test Metrics

## 🚨 Troubleshooting

### Häufige Probleme

#### Tests schlagen fehl
```bash
# Datenbank-Verbindung prüfen
docker-compose ps

# Dependencies installieren
pip install -r requirements.txt
npm install

# Test-Datenbank zurücksetzen
pytest --create-db
```

#### Performance-Tests zu langsam
```bash
# Nur schnelle Tests
pytest tests/performance/ -m "not slow"

# Parallel ausführen
pytest -n auto
```

#### E2E-Tests instabil
```bash
# Retry erhöhen
npx playwright test --retries=3

# Headless deaktivieren
npx playwright test --headed
```

## 📚 Best Practices

### Test-Schreibung
1. **AAA-Pattern**: Arrange, Act, Assert
2. **Descriptive Names**: Klare Test-Namen
3. **Single Responsibility**: Ein Test, ein Szenario
4. **Independent Tests**: Keine Abhängigkeiten
5. **Fast Tests**: Unit Tests < 1s

### Test-Daten
1. **Realistic Data**: Echte Datenstrukturen
2. **Minimal Data**: Nur notwendige Daten
3. **Isolated Data**: Keine Seiteneffekte
4. **Cleanup**: Nach Tests aufräumen

### Performance-Tests
1. **Baseline Metrics**: Referenzwerte definieren
2. **Realistic Load**: Echte Nutzungsszenarien
3. **Monitoring**: Metriken überwachen
4. **Regression Detection**: Performance-Abfälle erkennen

---

**Vollständige Test-Suite für Enterprise-Grade Qualitätssicherung**
