# Simple Dockerfile for demo
# Use a base Python image
FROM python:3.10-slim

# Copy application code
WORKDIR /app
COPY ./rag-demo /app/rag-demo
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Start streamlit app
WORKDIR /app/rag-demo
EXPOSE 8501
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
