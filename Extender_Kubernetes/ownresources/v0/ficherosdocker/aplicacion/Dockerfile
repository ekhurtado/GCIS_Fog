FROM python:3.10-alpine
RUN pip install kubernetes
RUN pip install datetime
COPY ./application_definition.yaml /
COPY ./mi_watcher_aplicaciones_v2.py /
COPY ./mi_controlador_aplicaciones_v2.py /
COPY ./tipos.py /
CMD python3 mi_controlador_aplicaciones_v2.py
