FROM python:3.13-alpine
WORKDIR /app
COPY req.txt req.txt
RUN pip install -r req.txt
COPY . .
EXPOSE 8080
ENTRYPOINT [ "python", "backend.py" ]