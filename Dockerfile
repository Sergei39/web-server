FROM python:3.8

#COPY httptest /var/www/html
COPY . .
COPY ./data /var/www/html

EXPOSE 80

CMD python3 main.py etc/httpd.conf
