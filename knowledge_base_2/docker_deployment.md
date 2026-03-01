# Dockerizing Python Applications

Summary:
Creates Dockerfile for Python app.
Exposes ports and installs dependencies.
Used for container deployment.

---

FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]