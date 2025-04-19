FROM mcr.microsoft.com/playwright/python:v1.51.0-noble
WORKDIR /app
COPY req.txt req.txt
RUN python -m pip install --upgrade pip
RUN pip install -r req.txt
RUN playwright install
COPY . .
EXPOSE 8080
ENTRYPOINT [ "python", "backend.py" ]