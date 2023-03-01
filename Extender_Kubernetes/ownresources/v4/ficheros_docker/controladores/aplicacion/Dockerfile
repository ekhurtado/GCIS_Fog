FROM python:3.10-alpine
RUN pip install kubernetes
RUN pip install datetime
COPY ./application_definition.yaml /CRD/
COPY ./mi_controlador_aplicaciones.py /
COPY ./tipos.py /
CMD python3 mi_controlador_aplicaciones.py
