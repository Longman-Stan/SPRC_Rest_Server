FROM python:3.6
COPY requirements.txt /tmp
RUN pip install -U setuptools
RUN pip install -r /tmp/requirements.txt
COPY Server/ /app
WORKDIR /app
CMD ["python", "server.py"]
