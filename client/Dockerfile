# Use a lightweight web server image
FROM nginx:alpine

# Remove the default NGINX website
RUN rm -rf /usr/share/nginx/html/*

# Copy your static files (index.html and others) into the container
COPY index.html /usr/share/nginx/html/

# Expose port 80 (NGINX default)
EXPOSE 80

# NGINX is started automatically by the base image