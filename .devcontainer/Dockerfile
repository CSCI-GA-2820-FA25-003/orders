# Image for a NYU Lab development environment
FROM rofrano/nyu-devops-base:su25

USER root

# Set up the Python development environment
WORKDIR /app
COPY Pipfile Pipfile.lock ./
RUN sudo python -m pip install --upgrade pip pipenv && \
    sudo pipenv install --system --dev

RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates chromium-driver firefox-esr python3-selenium

# Install user mode tools
COPY .devcontainer/scripts/install-tools.sh /tmp/
RUN cd /tmp && bash ./install-tools.sh