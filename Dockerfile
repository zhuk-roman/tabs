FROM tiangolo/uwsgi-nginx-flask:python3.7

# LABEL Author="Zhuk Roman"
# LABEL E-mail="zhuk.roman.v@gmail.com"
# LABEL version="0.0.1"

# ENV PYTHONDONTWRITEBYTECODE 1
# ENV FLASK_ENV "development"
# ENV FLASK_DEBUG True
# ENV FLASK_APP "run.py"

# RUN mkdir /app
WORKDIR /app

COPY requirements.txt uwsgi.ini /app/
COPY tabs /app/tabs
COPY static /app/static

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 80

# CMD tree /app
# CMD python run.py
