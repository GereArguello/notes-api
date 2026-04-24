# 1. Build stage
FROM node:20 AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .
RUN npm run build

# 2. Production stage
FROM nginx:latest

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80