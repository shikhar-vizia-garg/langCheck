# Use an official Python runtime as a base image
FROM python:3.11

# Install system dependencies (including PortAudio)
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    libportaudio2 \
    libportaudio-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy all project files into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install sounddevice

# Expose Flask (5000) and Streamlit (8501) ports
EXPOSE 5000
EXPOSE 8501

# Start both Flask & Streamlit together
CMD ["sh", "-c", "python main.py & streamlit run main.py --server.port=8501 --server.address=0.0.0.0"]