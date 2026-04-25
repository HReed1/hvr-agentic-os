# Use a pure Python base image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the actual workspace over so the tests have the scripts to execute 
# In CI, this would normally be a volume mount, but for isolation, we bake it into the base image
COPY requirements.txt .

# Install all necessary python dependencies globally to circumvent direnv/venv requirements
RUN pip install --no-cache-dir -r requirements.txt pytest pytest-xdist pexpect

# Install the Gemini CLI directly into the linux image via npm
RUN npm install -g @google/gemini-cli
RUN mkdir -p /root/.gemini

# Copy the rest of the codebase into the image 
COPY . .

# Set up the ephemeral RAM disk mount point
RUN mkdir -p /tmp/eval_spaces
