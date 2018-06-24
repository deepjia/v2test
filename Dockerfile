FROM python:latest

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && apt update \
    && apt install google-chrome-stable \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD [ "gunicorn", "-w", "4", "-b", ":8080", "manager:app"]