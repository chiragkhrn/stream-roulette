FROM node:18 AS frontend

WORKDIR /app/frontend
COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install
COPY frontend .
RUN yarn build

FROM node:18 AS backend

WORKDIR /app/backend
COPY backend ./
COPY --from=frontend /app/frontend/build ./public

CMD ["node", "index.js"]
