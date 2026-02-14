FROM python:3.13.1-alpine
WORKDIR /app

COPY requirements.txt .
RUN python -m pip --upgrade pip && python -m pip install -r requirements.txt
COPY . .

EXPOSE 8000
ENTRYPOINT [ "python", "server.py" ]