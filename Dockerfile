FROM tiangolo/uwsgi-nginx-flask:python3.7


WORKDIR /root
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip aws/

COPY ./.aws /root/.aws
COPY ./aws_credentials /root/.aws/credentials

WORKDIR /app

COPY requirements.txt uwsgi.ini /app/
COPY tabs /app/tabs
COPY static /app/static

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 80
