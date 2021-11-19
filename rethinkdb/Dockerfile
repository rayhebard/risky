FROM rethinkdb

RUN apt-get update && apt install python3-pip -y

RUN pip3 install rethinkdb

VOLUME ["/data"]

WORKDIR /data

CMD ["rethinkdb", "--bind", "all"]

#   process cluster webui
EXPOSE 28015 29015 8080
