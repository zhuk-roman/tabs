FROM python:3.7.5

# LABEL Author="Zhuk Roman"
# LABEL E-mail="zhuk.roman.v@gmail.com"
LABEL version="0.0.1"

# ENV PYTHONDONTWRITEBYTECODE 1
# ENV FLASK_ENV "development"
# ENV FLASK_DEBUG True
ENV FLASK_APP "run.py"

RUN mkdir /app
WORKDIR /app

COPY requirements.txt run.py /app/
COPY tabs /app/tabs

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 5000

CMD tree /app
CMD python run.py