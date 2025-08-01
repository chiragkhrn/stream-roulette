# ---------- FRONTEND ----------
FROM node:18 AS frontend

WORKDIR /app/frontend

COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install
COPY frontend .
RUN yarn build

# ---------- BACKEND ----------
FROM node:18 AS backend

WORKDIR /app/backend

COPY backend/package.json ./
RUN npm install
COPY backend .

# ✅ If you're serving frontend via backend
COPY --from=frontend /app/frontend/dist ./public

# Start backend server
CMD ["node", "index.js"]
