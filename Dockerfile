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
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    libxcb1 \
    libxcb-util1 \
    libxcb-image0 \
    libxcb-icccm4 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-shm0 \
    libxcb-sync1 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    libfontconfig1 \
    libdbus-1-3 \
    libsm6 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxrandr2 \
    libxi6 \
    libxtst6 \
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
