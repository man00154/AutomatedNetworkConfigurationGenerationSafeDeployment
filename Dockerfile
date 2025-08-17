# Use an official lightweight Python image as a base
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt ./

# Install the dependencies from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Streamlit application code into the container
COPY . .

# Expose the default Streamlit port
EXPOSE 8501

# Command to run the Streamlit application
# We use --server.address=0.0.0.0 to make it accessible from outside the container
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
