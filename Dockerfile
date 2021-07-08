FROM python:3.7.1-alpine3.8

RUN pip install --user pipenv

ENV PATH /root/.local/bin:${PATH}
ENV SHELL sh

WORKDIR /app

COPY * ./

RUN pipenv check

RUN pipenv install

CMD ["pipenv", "run", "python", "assess-rest-api.py"]
