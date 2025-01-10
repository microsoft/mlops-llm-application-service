FROM ubuntu:22.04

ARG USERNAME=vscode

USER root

RUN apt-get update -y && apt-get install -y sudo wget gnupg software-properties-common curl bash && \
    # Download and install Miniconda
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/miniconda && \
    rm /tmp/miniconda.sh && \
    # Create a non-root user
    useradd -m -s /bin/bash $USERNAME && \
    echo "$USERNAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME && \
    # Change ownership of Miniconda to the non-root user
    chown -R $USERNAME:$USERNAME /opt/miniconda

ENV PATH=/opt/miniconda/bin:$PATH

# Install dependencies
WORKDIR /home/$USERNAME

# Install Azure CLI
RUN sudo apt-get update && sudo apt-get install -y gnupg software-properties-common curl && \
    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash && \
    az config set extension.use_dynamic_install=yes_without_prompt && \
    az extension add -n ml

COPY python/requirements.txt .

# Create Conda environment and install Python dependencies
RUN conda create -n llm-env python=3.12 pip=23.2 -q -y && \
    conda run -n llm-env pip install -r requirements.txt && \
    conda clean -a -y

RUN echo "conda activate llm-env" >> /home/$USERNAME/.bashrc