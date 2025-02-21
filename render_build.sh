#!/bin/bash
echo "Installing system dependencies..."
apt-get update && apt-get install -y libportaudio2 libportaudio-dev

echo "Installing Python dependencies..."
pip install -r requirements.txt
pip install sounddevice  # Install after PortAudio is available