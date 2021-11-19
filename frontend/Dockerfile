FROM node:17-alpine

RUN apk update && apk add bash && apk add python3 && apk add build-base && apk add python2
# make the 'frontend' folder the current working directory
WORKDIR /frontend

COPY . .

# copy both 'package.json' and 'package-lock.json' (if available)
COPY package.json .

# install project dependencies
RUN npm install -g npm parcel
# RUN npm install
RUN npm install

# copy project files and folders to the current working directory (i.e. 'app' folder)


#expose ports for server and websocket
EXPOSE 80
EXPOSE 1234
