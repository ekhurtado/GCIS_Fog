FROM python:3.10-alpine
RUN pip install kubernetes
RUN pip install kafka-python
COPY ./componente_productor_2.py /
CMD python3 componente_productor_2.py
