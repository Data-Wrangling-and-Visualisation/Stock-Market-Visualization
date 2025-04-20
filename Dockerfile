FROM mcr.microsoft.com/playwright/python:v1.51.0-noble

WORKDIR /app

# Copy requirements first for better caching
COPY src/req.txt requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN playwright install

# Copy the database and other files
COPY src/ src/
COPY data/ data/
COPY moex.db ./

# Set working directory to src where the main application is
WORKDIR /app/src

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application
CMD ["python", "backend.py"] 