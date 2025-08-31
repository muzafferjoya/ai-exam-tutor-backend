# backend/Dockerfile
FROM python:3.11.8-slim

WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Install FastAPI, Uvicorn, and supabase.py (directly, guaranteed to work)
RUN pip install --no-cache-dir \
    fastapi==0.110.0 \
    uvicorn==0.29.0 \
    requests==2.31.0 \
    pydantic==2.5.0 \
    python-multipart==0.0.6 \
    supabase.py==2.18.1

# Copy only main.py and database.py (or all .py files)
COPY main.py database.py ai_engine.py ./


# Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
