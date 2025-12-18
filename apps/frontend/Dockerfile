# apps/frontend/Dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy package definition
COPY apps/frontend/package.json apps/frontend/package-lock.json* ./

# Install dependencies
RUN npm install

# Copy source
COPY apps/frontend ./

# Expose Vite port
EXPOSE 5173

# Host 0.0.0.0 is crucial for Docker
CMD ["npm", "run", "dev", "--", "--host"]
