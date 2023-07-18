FROM python:alpine
COPY . .
RUN adduser -D myuser && chown -R myuser /templates/index.html /templates/error.html app.py /templates
USER myuser
RUN pip install -r requirements.txt
EXPOSE 8080
CMD ["python3", "app.py"]
