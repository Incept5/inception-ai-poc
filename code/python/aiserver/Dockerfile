FROM python:3.11

WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# We'll install dependencies at build time
COPY requirements.txt .
COPY constraints.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt -c constraints.txt

# Install Playwright and its dependencies
RUN playwright install chromium
RUN playwright install-deps chromium

# We're not copying any code files here, as they'll be mounted at runtime

CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]