# =============================================================================
# AI-MOS Frontend — Production Multi-Stage Dockerfile
# =============================================================================

# --- Stage 1: Build Layer ---
FROM node:20-alpine AS build

WORKDIR /app

# Copy dependency specifications
COPY package.json package-lock.json ./

# Install packages exactly as locked in package-lock.json
RUN npm ci

# Copy full frontend source code
COPY . .

# Compile TypeScript and build production assets (builds to dist/)
RUN npm run build

# --- Stage 2: Production Web Server Layer ---
FROM nginx:1.25-alpine

# Remove default Nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom Nginx configuration for client-side routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy compiled static assets from build stage to Nginx serve root
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
