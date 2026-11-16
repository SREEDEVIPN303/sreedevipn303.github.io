# Django Sample Projects

Two small, tested Django projects written as portfolio samples (not employer code).

| App | What it shows |
|---|---|
| `sensorhub` | IoT monitoring: devices POST readings to a REST endpoint (API-key protected); a dashboard charts them and flags threshold alerts. |
| `taskboard` | Kanban-style task manager: JSON CRUD API with validation, CSRF-protected front end. |

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo          # demo sensors + readings
python manage.py runserver
```
- SensorHub: http://127.0.0.1:8000/sensorhub/
- TaskBoard: http://127.0.0.1:8000/taskboard/

## Push a reading from a device
```bash
curl -X POST http://127.0.0.1:8000/sensorhub/api/sensors/1/readings/ \
  -H "Content-Type: application/json" -H "X-API-Key: demo-device-key" \
  -d '{"value": 27.4}'
```

## Tests
```bash
python manage.py test      # 11 tests
```

## Use MySQL instead of SQLite
```bash
pip install mysqlclient
export DB_ENGINE=mysql DB_NAME=devfolio DB_USER=root DB_PASSWORD=secret
python manage.py migrate
```
Set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0` and `DEVICE_API_KEY` before any real deployment.
