FROM python:3.8

#COPY httptest /var/www/html
COPY . /app
COPY . /var/www

WORKDIR /app
RUN pip install http-parser

EXPOSE 80

CMD python3 main.py etc/httpd.conf
