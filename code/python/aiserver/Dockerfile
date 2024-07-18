FROM python:3.11

WORKDIR /app

# We'll install dependencies at build time
COPY requirements.txt .
COPY constraints.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt -c constraints.txt

# We're not copying any code files here, as they'll be mounted at runtime

CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]