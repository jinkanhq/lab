FROM python:slim
WORKDIR /website
RUN pip install -i https://mirrors.bfsu.edu.cn/pypi/web/simple pelican[markdown] pelican-webassets cssmin pelican-seo
