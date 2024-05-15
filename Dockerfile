# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container
COPY . .

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libx11-dev \
    libxext-dev \
    libxrender-dev \
    libxkbcommon-x11-0 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Verify the installation
RUN pip list
RUN python -c "from PySide2.QtCore import QObject, Signal; print('PySide2 is installed')"
RUN python -c "from qtpy.QtCore import QObject, Signal; print('Qt bindings are working')"

# Expose the port
EXPOSE 80

# Run Ryven when the container launches
CMD ["python", "./ryven/ryven/main/Ryven.py"]
