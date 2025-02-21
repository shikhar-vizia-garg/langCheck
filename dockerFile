# Use the official Python image
FROM python:3.11

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libportaudio2 \
    libportaudio-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy project files
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