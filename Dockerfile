FROM python:3.12-alpine
 
# Create app directory
WORKDIR /app
 
# Install app dependencies
COPY . /app
 
RUN pip install --no-cache-dir -r requirements.txt 

ENV FLASK_APP=main.py

EXPOSE 5000
CMD [ "flask", "run","--host","0.0.0.0","--port","5000"]
