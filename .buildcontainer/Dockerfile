FROM ubuntu:22.04

# Initialize arguments
ARG USERNAME=vscode

ENV CONDA_ENVIRONMENT_PATH=/opt/miniconda/envs/mlopsllm-env
ENV CONDA_DEFAULT_ENVIRONMENT=$CONDA_ENVIRONMENT_PATH
ENV PATH $CONDA_DEFAULT_ENVIRONMENT/bin:$PATH

# Setup user for sudo
USER root

# Update apt-get, install sudo and create a non-root user
RUN apt-get update -y && apt-get dist-upgrade -y && apt-get install -y sudo \
    && useradd -m -s /bin/bash $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME \
    && chown -R $USERNAME:$USERNAME /opt/miniconda

#Use the non-root user
USER $USERNAME

# Install dependencies
WORKDIR /home/$USERNAME

# Install Azure CLI
RUN sudo apt-get update \
    && sudo apt-get install -y gnupg software-properties-common libc6 \
    && curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash \
    && az config set extension.use_dynamic_install=yes_without_prompt \
    && az extension add -n ml

COPY python/requirements.txt .

RUN conda init bash \
    && conda create -n mlopsllm-env python=3.12 pip=23.0.1 -q -y \
    && conda run -n mlopsllm-env pip install --no-cache-dir -r requirements.txt \
    && conda clean -a -y

RUN echo "conda activate mlopsllm-env" >> /home/$USERNAME/.bashrc