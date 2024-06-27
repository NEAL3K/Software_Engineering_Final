# Use the official continuumio/miniconda3 image as base
FROM continuumio/miniconda3

# Set working directory
WORKDIR /code

# Copy the requirements.txt file
COPY requirements.txt /code/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /code/

# Expose the port the app runs on
EXPOSE 5000

# Run the application
CMD ["sh", "-c", "python manage.py migrate && python manage.py loaddata /code/Final_proj.sql && python manage.py runserver 0.0.0.0:5000"]
