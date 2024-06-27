# Use the official continuumio/miniconda3 image as base
FROM continuumio/miniconda3

# Set working directory
WORKDIR /code

# Copy the environment.yml file
COPY environment.yml /code/

# Create the environment
RUN conda env create -f environment.yml

# Make RUN commands use the new environment
SHELL ["conda", "run", "-n", "supermarket", "/bin/bash", "-c"]

# Copy the rest of the application code
COPY . /code/

# Expose the port the app runs on
EXPOSE 5000

# Run the application
CMD ["conda", "run", "-n", "supermarket", "sh", "-c", "python manage.py migrate && python manage.py loaddata /code/Final_proj.sql && python manage.py runserver 0.0.0.0:5000"]
