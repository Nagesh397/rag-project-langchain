FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY pyproject.toml .
COPY src ./src
COPY scripts ./scripts
COPY gradio_app.py .
COPY data ./data
COPY Extra ./Extra
ENV PYTHONPATH=/app/src
CMD ["python", "gradio_app.py"]