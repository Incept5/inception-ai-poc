FROM python:3.9

WORKDIR /app

# We'll install dependencies at build time
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# We're not copying any code files here, as they'll be mounted at runtime

CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]