# ---------- FRONTEND BUILD ----------
FROM node:18 AS frontend
WORKDIR /app/frontend

# Install frontend dependencies and build
COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install
COPY frontend .
RUN yarn build

# ---------- BACKEND ----------
FROM python:3.10-slim AS backend
WORKDIR /app

# Install backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend .

# Copy frontend build into backend (to serve static files if needed)
COPY --from=frontend /app/frontend/build ./frontend_build

# Expose your backend port (adjust if needed)
EXPOSE 5000

# Run the backend
CMD ["python", "server.py"]
