FROM python:3.6

RUN mkdir -p /Django_MallWeb

RUN apt-get update && \
    apt-get install -y vim && \
    apt-get install -y net-tools && \
	rm -rf /var/lib/apt/lists/*

COPY . /Django_MallWeb

WORKDIR /Django_MallWeb

RUN pip3 install -r requirements.txt

EXPOSE 8000

CMD ["python3 ./meiduo_mall/manage.py runserver 0.0.0.0:8000"]