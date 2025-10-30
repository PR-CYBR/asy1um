FROM cowrie/cowrie:latest

# Copy custom configuration
COPY cowrie.cfg /cowrie/cowrie-git/etc/cowrie.cfg
COPY userdb.txt /cowrie/cowrie-git/etc/userdb.txt

# Expose SSH and Telnet ports
EXPOSE 2222 2223

# Set working directory
WORKDIR /cowrie/cowrie-git

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD nc -z localhost 2222 || exit 1

# Run Cowrie
CMD ["cowrie", "start", "-n"]
