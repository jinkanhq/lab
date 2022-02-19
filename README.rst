人间实验室
====================

「人间」的又一个用意不明的试验性项目

https://lab.jinkan.org


构建
-----------

::

    $ git -C themes/kagami-pelican pull || git clone https://github.com/jinkanhq/kagami-pelican themes/kagami-pelican
    $ docker build . -t lab-pelican:slim
    $ docker run -it --rm -v $(pwd):/website lab-pelican:slim pelican
