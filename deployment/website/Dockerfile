# ============================================
#  Website Dockerfile — Multi-stage build
#  Builds both backend and frontend
# ============================================

# ── Stage 1: Frontend Build ──
FROM node:18-alpine AS frontend-build
WORKDIR /app
COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install --frozen-lockfile
COPY frontend/ ./
ARG REACT_APP_BACKEND_URL
ARG REACT_APP_TURNSTILE_SITE_KEY
ARG REACT_APP_PAYHERE_BASE_URL
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL
ENV REACT_APP_TURNSTILE_SITE_KEY=$REACT_APP_TURNSTILE_SITE_KEY
ENV REACT_APP_PAYHERE_BASE_URL=$REACT_APP_PAYHERE_BASE_URL
RUN yarn build

# ── Stage 2: Frontend Serve ──
FROM nginx:alpine AS frontend
COPY --from=frontend-build /app/build /usr/share/nginx/html
RUN echo 'server { \
    listen 80; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { try_files $uri $uri/ /index.html; } \
}' > /etc/nginx/conf.d/default.conf
EXPOSE 80

# ── Stage 3: Backend ──
FROM python:3.11-slim AS backend
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
EXPOSE 8002
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002", "--workers", "2"]
