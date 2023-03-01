FROM python:3.10-alpine
RUN pip install kubernetes
RUN pip install datetime
COPY ./gestor_eventos.py /
COPY ./tipos.py /
CMD python3 gestor_eventos.py
