FROM python:3.9-slim-bullseye
RUN useradd -u 8877 --create-home userunner
ENV PATH="/home/userunner/.local/bin:$PATH" 
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir  -r requirements.txt 
USER userunner
COPY --chown=userunner . /app/
# HEALTHCHECK --interval=1800s --timeout=5s --start-period=5s --retries=3 CMD curl --fail http://localhost/healthcheck || exit 1
CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]
