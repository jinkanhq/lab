FROM python:slim
WORKDIR /website
RUN pip install pelican[markdown] pelican-webassets cssmin
