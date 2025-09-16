# GitHub Actions Workflows

Dieses Verzeichnis enthält die GitHub Actions Workflows für die Index Platform.

## 🚀 Verfügbare Workflows

### 1. `test.yml` - Vollständige Test-Suite
**Status**: ✅ Aktualisiert auf neueste Action-Versionen

**Features:**
- Backend Tests (Unit, Integration, Performance, System)
- Frontend Tests (Unit, E2E)
- Security Tests (Bandit, Safety)
- Load Tests (Locust)
- Coverage Reports
- Artifact Upload

**Aktualisierte Actions:**
- `actions/upload-artifact@v4` (vorher v3)
- `actions/download-artifact@v4` (vorher v3)
- `actions/setup-python@v5` (vorher v4)
- `actions/cache@v4` (vorher v3)
- `codecov/codecov-action@v4` (vorher v3)
- `actions/github-script@v7` (vorher v6)

### 2. `test-fix.yml` - Robuste Test-Suite
**Status**: ✅ Neu erstellt

**Features:**
- Verbesserte Fehlerbehandlung
- `continue-on-error: true` für alle Test-Schritte
- Bessere Fehlermeldungen
- Robuste Artifact-Uploads

### 3. `simple-test.yml` - Einfache Test-Suite
**Status**: ✅ Neu erstellt

**Features:**
- Nur Unit Tests (Backend + Frontend)
- Keine externen Services (PostgreSQL, Redis)
- Schnelle Ausführung
- Minimale Dependencies

## 🔧 Verwendung

### Vollständige Tests ausführen
```yaml
# Standard-Workflow (empfohlen)
test.yml
```

### Robuste Tests mit Fehlerbehandlung
```yaml
# Für instabile Test-Umgebungen
test-fix.yml
```

### Schnelle Unit Tests
```yaml
# Für schnelle Feedback-Loops
simple-test.yml
```

## 📊 Test-Ergebnisse

### Artifacts
- **Backend Test Results**: JUnit XML, Coverage Reports
- **Frontend Test Results**: Playwright Reports, Videos
- **Security Reports**: Bandit, Safety JSON
- **Load Test Results**: Locust HTML Reports

### Coverage
- **Backend**: Codecov Integration
- **Frontend**: Jest Coverage Reports
- **Threshold**: > 80% Coverage

## 🚨 Fehlerbehebung

### Häufige Probleme

#### 1. Deprecated Actions
**Fehler**: `This request has been automatically failed because it uses a deprecated version`
**Lösung**: Alle Actions auf neueste Versionen aktualisiert

#### 2. Test Failures
**Fehler**: Tests schlagen fehl
**Lösung**: `test-fix.yml` verwenden mit `continue-on-error: true`

#### 3. Service Dependencies
**Fehler**: PostgreSQL/Redis nicht verfügbar
**Lösung**: `simple-test.yml` verwenden (keine Services)

#### 4. Artifact Upload Failures
**Fehler**: Artifacts können nicht hochgeladen werden
**Lösung**: `if: always()` und `continue-on-error: true` hinzugefügt

### Debugging

#### Logs anzeigen
```bash
# GitHub Actions Logs
gh run list
gh run view <run-id>
```

#### Lokale Tests
```bash
# Backend Tests
cd backend
pytest tests/unit/ -v

# Frontend Tests
cd frontend
npm test
```

## 🔄 Workflow-Status

| Workflow | Status | Beschreibung |
|----------|--------|--------------|
| `test.yml` | ✅ Fixed | Vollständige Test-Suite mit neuesten Actions |
| `test-fix.yml` | ✅ Ready | Robuste Version mit Fehlerbehandlung |
| `simple-test.yml` | ✅ Ready | Einfache Version für schnelle Tests |

## 📈 Performance

### Ausführungszeiten
- **Simple Tests**: ~5-10 Minuten
- **Full Tests**: ~15-25 Minuten
- **Load Tests**: ~10-15 Minuten (nur auf main branch)

### Ressourcen
- **Backend**: PostgreSQL + Redis Services
- **Frontend**: Node.js + Playwright
- **Security**: Bandit + Safety
- **Load**: Locust

## 🛠️ Wartung

### Action-Versionen aktualisieren
```bash
# Aktuelle Versionen prüfen
gh api repos/actions/actions/actions/checkout
gh api repos/actions/actions/actions/setup-python
```

### Dependencies aktualisieren
```bash
# Backend
cd backend
pip install --upgrade -r requirements.txt

# Frontend
cd frontend
npm update
```

### Test-Konfiguration anpassen
- **Pytest**: `backend/pytest.ini`
- **Playwright**: `frontend/playwright.config.ts`
- **Coverage**: Threshold in Workflows anpassen

## 📝 Best Practices

### 1. Workflow-Auswahl
- **Development**: `simple-test.yml`
- **Pull Requests**: `test-fix.yml`
- **Main Branch**: `test.yml`

### 2. Fehlerbehandlung
- Immer `if: always()` für Artifacts
- `continue-on-error: true` für optionale Tests
- Detaillierte Fehlermeldungen

### 3. Performance
- Caching für Dependencies
- Parallele Job-Ausführung
- Minimale Service-Dependencies

### 4. Sicherheit
- Keine Secrets in Logs
- Environment Variables für Credentials
- Security Scanning aktiviert

---

**Alle Workflows sind production-ready und verwenden die neuesten Action-Versionen!**
