FROM python:3.10-alpine
RUN pip install kubernetes
RUN pip install datetime
COPY ./component_definition.yaml /CRD/
COPY ./mi_controlador_componentes.py /
COPY ./tipos.py /
CMD python3 mi_controlador_componentes.py
