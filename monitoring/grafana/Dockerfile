FROM grafana/grafana:latest

# Copy provisioning configurations
COPY provisioning /etc/grafana/provisioning

# Set environment variables
ENV GF_SECURITY_ADMIN_USER=admin
ENV GF_SECURITY_ADMIN_PASSWORD=asylum_admin_2024
ENV GF_USERS_ALLOW_SIGN_UP=false
ENV GF_SERVER_ROOT_URL=http://localhost:3000

EXPOSE 3000
