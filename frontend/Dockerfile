# Build stage
# Cache bust: 2026-01-30-v3-force-rebuild
FROM node:20-alpine AS builder

WORKDIR /app

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Build arg for API URL (baked in at build time)
# Default to environment variable or Railway backend URL for production builds
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL:-https://your-backend-url.up.railway.app}
ENV NODE_ENV=production

# Build the app (with logging to verify env vars)
RUN echo "=== Building frontend ===" && \
    echo "VITE_API_BASE_URL=$VITE_API_BASE_URL" && \
    echo "NODE_ENV=$NODE_ENV" && \
    pnpm build

# Production stage
FROM nginx:alpine

# Copy nginx config template
COPY nginx.conf /etc/nginx/templates/default.conf.template

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Railway sets PORT env var, nginx:alpine supports envsubst via templates
ENV PORT=80

# Expose port
EXPOSE 80

# nginx:alpine automatically processes templates in /etc/nginx/templates/
# and substitutes environment variables
CMD ["nginx", "-g", "daemon off;"]
