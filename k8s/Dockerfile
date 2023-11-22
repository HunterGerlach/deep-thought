FROM registry.access.redhat.com/ubi8/python-311:1-35

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install poetry

COPY . /app/

RUN poetry install

EXPOSE 8000

CMD ["make", "run"]
