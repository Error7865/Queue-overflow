FROM python:3.12-alpine

ENV FLASK_APP flasky.py
ENV FLASK_CONFIG docker

RUN adduser -D flasky
USER flasky
WORKDIR /home/flasky
COPY requirments requirments
RUN py -m venv vir_env
RUN vir_env/bin/pip install -r requirments/docker.txt

COPY app app
COPY flasky.py config.py boot.sh ./

# runtime configuration 
EXPOSE 5000
ENTRYPOINT [ "./boot.sh" ]