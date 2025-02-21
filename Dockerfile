# Use the official Python image
FROM python:3.11

# Set environment variables to prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1

# Update and install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libportaudio2 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir sounddevice

# Expose Flask (5000) and Streamlit (8501) ports
EXPOSE 5000
EXPOSE 8501

# Start Flask and Streamlit
CMD ["sh", "-c", "python main.py & streamlit run main.py --server.port=8501 --server.address=0.0.0.0 --server.enableCORS=false"]