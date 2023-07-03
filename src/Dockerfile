FROM python:alpine

#ENV VIRTUAL_ENV=/home/ariel/something/web/webproject/myEnv
#RUN python3 -m venv $VIRTUAL_ENV
#ENV PATH="$VIRTUAL_ENV/bin:$PATH"


WORKDIR /app
RUN addgroup -S myuser && adduser -S myuser -G myuser
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
RUN chown -R myuser:myuser /app
USER myuser
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
