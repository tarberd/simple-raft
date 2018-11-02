FROM python:3

ADD server.py /
ADD requirements.txt /


RUN pip install -r requirements.txt

ENV FLASK_APP=server.py
EXPOSE 8080
CMD [ "python", "./server.py" ]