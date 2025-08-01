# Base image
FROM node:18 AS frontend

# Set working dir for frontend
WORKDIR /app/frontend

# Copy frontend files and install deps
COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install
COPY frontend .

# Build frontend
RUN yarn build

# --- Backend Stage ---
FROM node:18 AS backend

# Set working dir for backend
WORKDIR /app

# Copy backend files
COPY backend ./backend

# Install backend dependencies
WORKDIR /app/backend
COPY backend/package.json backend/package-lock.json ./
RUN npm install

# Copy frontend build to backend/public (if serving frontend from backend)
COPY --from=frontend /app/frontend/dist ./public

# Start server (adjust path if needed)
CMD ["node", "index.js"]
