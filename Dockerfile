# Image for a NYU Lab development environment
FROM rofrano/nyu-devops-base:su25

# Set up the Python development environment
WORKDIR /app
COPY Pipfile Pipfile.lock ./
RUN sudo python -m pip install --upgrade pip pipenv && \
    sudo pipenv install --system --dev

# Install user mode tools
COPY .devcontainer/scripts/install-tools.sh /tmp/
RUN cd /tmp && bash ./install-tools.sh

# Copy application code
COPY service /app/service
COPY wsgi.py ./

# Default fallback to SQLite (for local/dev convenience only; K8s will override via Deployment env)
ENV DATABASE_URI=sqlite:////tmp/orders.db

# Expose application port
EXPOSE 8080

# Start the Flask app with Gunicorn (wsgi:app)
CMD ["gunicorn","--bind","0.0.0.0:8080","--log-level=info","wsgi:app"]