# Minimal Dockerfile for running the app. This image is intentionally small and
# only used as an example in the scaffold.

FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONUNBUFFERED=1
CMD ["python", "-m", "autopilot"]
