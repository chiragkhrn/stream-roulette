### STAGE 1: Build React frontend ###
FROM node:18 AS frontend

WORKDIR /app/frontend

# Install dependencies and build
COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install

COPY frontend .
RUN yarn build


### STAGE 2: Backend with Python ###
FROM python:3.10-slim AS backend

WORKDIR /app

# Install backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend .

# Copy built frontend (from stage 1)
COPY --from=frontend /app/frontend/build ./frontend_build

# Expose port (adjust if needed)
EXPOSE 5000

# Run the backend server
CMD ["python", "server.py"]
