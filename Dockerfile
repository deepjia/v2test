FROM python:latest

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && apt-get update \
    && apt-get install -y google-chrome-stable

COPY . .

EXPOSE 8080

CMD [ "gunicorn", "-w", "4", "-b", ":8080", "manager:app"]