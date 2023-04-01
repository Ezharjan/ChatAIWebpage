FROM python:3.8.16
WORKDIR /code
COPY ./  /code

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

CMD ["python","/code/main.py","-u","root","-p","123456","--host","mongo地址","--port","27017","--databaseName","chatui"]

