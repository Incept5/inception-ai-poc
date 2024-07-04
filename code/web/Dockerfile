# Use the official Nginx image as a parent image
FROM nginx:alpine

# Remove the default Nginx configuration file
RUN rm /etc/nginx/conf.d/default.conf

# Expose port 9870
EXPOSE 9870

# Start Nginx when the container has provisioned
CMD ["nginx", "-g", "daemon off;"]