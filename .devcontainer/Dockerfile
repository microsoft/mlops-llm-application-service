FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye

# Install .NET SDK
RUN wget https://packages.microsoft.com/config/debian/11/packages-microsoft-prod.deb -O packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    apt-get update && \
    apt-get install -y dotnet-sdk-6.0

# Install Semantic Kernel SDK for C#
RUN dotnet new console -o /tmp/sk-csharp \
    && cd /tmp/sk-csharp \
    && dotnet add package Microsoft.SemanticKernel --version 0.9.2309.1-preview \
    && rm -rf /tmp/sk-csharp