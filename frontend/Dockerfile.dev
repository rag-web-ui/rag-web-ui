FROM node:18-alpine

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm@8

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 3000

# Start the development server, attention: this is for development, not for production
CMD ["pnpm", "dev"]
