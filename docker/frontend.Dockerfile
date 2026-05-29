FROM node:20-alpine AS base
WORKDIR /app

# Dev target — used by docker-compose.dev.yml
FROM base AS dev
COPY package*.json ./
RUN npm install
COPY . .
CMD ["npm", "run", "dev"]

# Build stage
FROM base AS builder
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Production
FROM node:20-alpine AS production
WORKDIR /app
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 3000
ENV HOSTNAME="0.0.0.0"
CMD ["node", "server.js"]
