FROM python:3.11.1

RUN apt-get update \
	&& apt-get install --no-install-recommends -y \
	nginx 

COPY nginx.conf /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log
	
RUN mkdir /app
WORKDIR /app
ADD . /app/
RUN chown -R www-data:www-data /app/newsfinder

ENV VIRTUAL_ENV=/app/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN apt install dos2unix
RUN dos2unix manage.py
RUN chmod +x manage.py start-service.sh
RUN ./manage.py makemigrations newsfinder
RUN ./manage.py migrate
RUN ./manage.py collectstatic --noinput

CMD ["/app/start-service.sh"]
