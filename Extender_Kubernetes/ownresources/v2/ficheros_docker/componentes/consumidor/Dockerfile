FROM python:3.10-alpine
RUN pip install kubernetes
RUN pip install kafka-python
COPY ./componente_consumidor.py /
CMD python3 componente_consumidor.py
