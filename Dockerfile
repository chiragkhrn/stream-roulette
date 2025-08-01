# === FRONTEND STAGE ===
FROM node:20 as frontend  

WORKDIR /app

COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install

COPY frontend/ ./
RUN yarn build


# === BACKEND STAGE ===
FROM python:3.10-slim as backend

WORKDIR /app

# Install Python deps
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./

# Copy frontend build from previous stage
COPY --from=frontend /app/dist ./frontend_build

# Expose port and run
EXPOSE 5000
CMD ["python", "server.py"]
