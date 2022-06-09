FROM node as build
WORKDIR /app
# caching package.json to avoid that npm install run everytime
COPY gui/package.json .
RUN npm install
COPY gui .
RUN npm run build

FROM nginx
COPY --from=build /app/build /usr/share/nginx/html