# NexusLang v2 Frontend - Dockerfile (Development)
FROM node:18-alpine

WORKDIR /app

# Install dependencies
RUN apk add --no-cache libc6-compat

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Set environment
ENV NEXT_TELEMETRY_DISABLED 1
ENV PORT 3000

# Run development server
CMD ["npm", "run", "dev"]

