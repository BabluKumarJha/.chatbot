# Use Python 3.10.11 slim image
FROM python:3.10.11-slim

# working directory inside container
WORKDIR /app

# Copy all project files into container
COPY . .

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data (if needed)
RUN python -m nltk.downloader punkt wordnet

# Expose Streamlit’s default port
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "app.py"]