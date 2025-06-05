# Build stage
FROM node:18 AS build
WORKDIR /app
COPY package.json ./
COPY public ./public
COPY src ./src
RUN npm install && npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80 