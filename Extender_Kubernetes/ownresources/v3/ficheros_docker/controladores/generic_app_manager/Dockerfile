FROM python:3.10-alpine
RUN pip install kubernetes
COPY ./generic_app_management_level_controller.py /
COPY ./tipos.py /
CMD python3 generic_app_management_level_controller.py
