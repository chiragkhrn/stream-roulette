# ---- FRONTEND ----
FROM node:20 AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install
COPY frontend .
RUN yarn build

# ---- BACKEND ----
FROM node:20 AS backend
WORKDIR /app/backend
COPY backend/package.json backend/package-lock.json ./
RUN npm install
COPY backend .

# Copy built frontend into backend/public
COPY --from=frontend /app/frontend/dist ./public

# Start server
CMD ["node", "index.js"]
