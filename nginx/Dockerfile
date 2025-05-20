FROM nginx:1.27.5

# Remove default Nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy your custom config
COPY nginx.conf /etc/nginx/conf.d
