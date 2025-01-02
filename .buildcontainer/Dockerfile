FROM ubuntu:22.04

# Initialize arguments
ARG USERNAME=vscode

# Setup user for sudo
USER root

# Install dependencies and Miniconda
RUN apt-get update -y && apt-get dist-upgrade -y && \
    apt-get install -y sudo wget bzip2 curl apt-transport-https lsb-release gnupg && \
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/miniconda && \
    rm /tmp/miniconda.sh && \
    /opt/miniconda/bin/conda init bash

# Add Miniconda to PATH
ENV PATH=/opt/miniconda/bin:$PATH

# Create user and set permissions
RUN useradd -m -s /bin/bash $USERNAME && \
    echo "$USERNAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME && \
    chown -R $USERNAME:$USERNAME /opt/miniconda

# Switch to non-root user
USER $USERNAME

# Set working directory
WORKDIR /home/$USERNAME

# Update PATH to include the Conda environment
ENV CONDA_ENVIRONMENT_PATH=/opt/miniconda/envs/mlopsllm-env
ENV PATH=$CONDA_ENVIRONMENT_PATH/bin:/opt/miniconda/bin:$PATH

# Copy requirements first to leverage Docker cache
COPY python/requirements.txt .

# Create Conda environment and install dependencies
RUN conda create -n mlopsllm-env python=3.12 pip=23.2 -y && \
    conda run -n mlopsllm-env pip install --no-cache-dir -r requirements.txt && \
    conda clean -a -y

# Install Azure CLI as root
USER root
RUN apt-get update && \
    apt-get install -y curl apt-transport-https lsb-release gnupg && \
    curl -sL https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    AZ_REPO=$(lsb_release -cs) && \
    echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ $AZ_REPO main" | tee /etc/apt/sources.list.d/azure-cli.list && \
    apt-get update && \
    apt-get install -y azure-cli

# Switch back to non-root user
USER $USERNAME

# Verify Azure CLI installation
RUN which az && az --version

# Activate Conda environment by default
RUN echo "conda activate mlopsllm-env" >> ~/.bashrc

# Set default command
CMD ["bash"]