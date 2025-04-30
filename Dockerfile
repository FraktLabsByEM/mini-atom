FROM python:3.9-slim

ENV DEBIAN_FRONTEND=noninteractive

# Update system dependencies
RUN apt update -y && \
    apt install -y \
    software-properties-common \
    curl \
    wget \
    git \
    nano \
    build-essential

# Install ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

COPY mini-atom/ /mini-atom/
COPY init.sh /usr/local/bin/init-docker.sh
RUN chmod +x /usr/local/bin/init-docker.sh

EXPOSE 2866

CMD ["/bin/bash", "/usr/local/bin/init-docker.sh"]