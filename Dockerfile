# syntax=docker/dockerfile:1
FROM python:3.8-alpine
WORKDIR /app
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN apk add --no-cache gcc musl-dev linux-headers libffi-dev openssh
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
RUN mv ./bin/* /usr/bin; rm -rf ./bin
CMD ["execapi"]
