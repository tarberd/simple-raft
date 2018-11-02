FROM python:3

ADD client.py /
ADD requirements.txt /

RUN pip install -r requirements.txt

CMD [ "python", "./client.py" ]