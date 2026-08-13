#!/bin/bash
set -e

echo "Digital Trophy MVP - Quick Start"
cd "$(dirname "$0")"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker не установлен. Установите: https://docs.docker.com/get-docker/"
    exit 1
fi

# Start PostgreSQL
echo "Starting PostgreSQL..."
docker compose up -d db

echo "Waiting for PostgreSQL..."
for i in {1..30}; do
    if docker compose exec -T db pg_isready -U trophy_user &> /dev/null; then
        echo "PostgreSQL готов!"
        break
    fi
    sleep 1
done

# Create Python virtualenv
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "========================================="
echo "Digital Trophy MVP готов!"
echo ""
echo "Запуск:"
echo "  cd /Users/vasilenko.a/Downloads/MVP"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "API docs: http://localhost:8000/api/docs"
echo "Frontend: http://localhost:8000"
echo "========================================="
