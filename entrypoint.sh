#!/bin/sh


# Jalankan server aplikasi utama
echo "Starting Uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8080