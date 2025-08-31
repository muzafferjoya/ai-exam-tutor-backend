FROM python:3.11.8-slim

WORKDIR /app

# Install system dependencies required for many Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libssl-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastapi==0.110.0 \
    uvicorn==0.29.0 \
    requests==2.31.0 \
    pydantic==2.5.0 \
    python-multipart==0.0.6 \
    supabase-py==2.18.1

# Copy your Python files
COPY main.py database.py ai_engine.py ./

# Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
