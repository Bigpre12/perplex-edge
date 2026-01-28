# Build stage
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
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Build the app
RUN pnpm build

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
