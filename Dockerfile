FROM python:3.4
ADD  server server
RUN  cd server && \
     pip3 install -e ".[test]" && \
     py.test --cov pi_mcqueen_server
