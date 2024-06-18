FROM nodered/node-red:3.0.2

RUN curl -L https://github.com/kubernetes/kompose/releases/download/v1.22.0/kompose-linux-amd64 -o kompose

RUN chmod +x kompose

USER root

RUN mv ./kompose /usr/local/bin/kompose

RUN npm install xmlhttprequest

RUN npm install node-red-contrib-xml-validate

RUN npm install libxmljs2-xsd

RUN npm install xslt-processor

COPY Application.xsd /xmlSchemas/Application.xsd

COPY appModelToAppDeliveryModel.xslt /xsltFiles/appModelToAppDeliveryModel.xslt

CMD node-red
