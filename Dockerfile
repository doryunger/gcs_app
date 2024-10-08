# Stage 1: Build the React app
FROM node:18-alpine AS  frontend-builder


# Set the working directory
RUN mkdir -p /app/frontend
WORKDIR /app/frontend

# Copy the package.json and package-lock.json files
COPY frontend/package*.json ./

# Copy the rest of the frontend code
COPY frontend/ ./

# Install dependencies
RUN npm install
# Expose the port for the frontend
EXPOSE 3000

# Start the React development server with nodemon
CMD ["npm", "start"]
# Stage 2: Set up the Python backend
FROM python:3.11-slim AS backend

WORKDIR /app/backend

# Copy the requirements file
COPY backend/requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY backend/ ./

# Expose the port for the backend
EXPOSE 8000
EXPOSE 8765
# Start the Python server
CMD ["python", "server.py"]
