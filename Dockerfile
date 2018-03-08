FROM python:3.4
ADD  server server
RUN  cd server && pip3 install -r requirements.txt . && py.test -s
