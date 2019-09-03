FROM python:2.7

COPY . /Kombucha_Control

WORKDIR /Kombucha_Control

RUN pip install -r requirements.txt

ENTRYPOINT ["python"]

CMD ["Create_Tables.py"]

CMD ["Kombucha_Control.py"]