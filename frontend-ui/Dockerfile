# frontend-ui/Dockerfile
# 1) Build con Node (Vite)
FROM node:20 AS build
WORKDIR /app
COPY package*.json /app/
RUN npm install
COPY . /app
RUN npm run build  # genera /app/dist

# 2) Nginx para servir estáticos y proxy /api -> backend
FROM nginx:alpine
# Config Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Copia estáticos
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
