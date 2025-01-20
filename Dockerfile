# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy only requirements.txt first (to leverage Docker caching)
COPY requirements.txt ./

# Create a virtual environment inside the container
RUN python -m venv venv \
    && . venv/bin/activate \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Ensure the virtual environment is used
ENV PATH="/usr/src/app/venv/bin:$PATH"

# Expose port 80 (if needed)
EXPOSE 80

# Define environment variable
ENV NAME DSProject

# Run the application with the virtual environment activated
CMD ["python", "ryven/ryven/main/Ryven.py"]
