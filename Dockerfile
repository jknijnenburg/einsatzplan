# For more information, please refer to https://aka.ms/vscode-docker-python
FROM mcr.microsoft.com/appsvc/python:3.12_20240502.3.tuxprod

EXPOSE 5000

# run pre-deploy, install packages
COPY azure-prebuild.sh .
RUN sh azure-prebuild.sh

# App Settings
ENV DEBUG=True
#ENV SQL_SERVER="hostname"
#ENV SQL_USER="username"
#ENV SQL_PASSWORD="password"
#ENV SQL_DATABASE="database_name"

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
