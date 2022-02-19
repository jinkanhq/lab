WordPress 的 Dockerize 避坑指南
###############################
:date: 2020-10-11 19:31
:author: yinian
:category: Uncategoried
:tags: Docker, Nginx, WordPress
:slug: dockerize-wordpress
:status: published
:feature: /images/2020/dockerize-wordpress-1.jpg
:abstract: Docker Hub 中 WordPress 项目的说明并未涵盖 fpm-alpine 的用法，笔者在这里做了小小的总结

前言
====

为了配合\ ``nginx``\ 食用风味更佳，减少磁盘空间占用，笔者选择了\ ``fpm-alpine``\ 系列标签的镜像，但 Docker Hub 中 WordPress 项目的说明只介绍了\ ``latest``\ 标签（同\ ``apache``\ 标签）的镜像用法，其中并未涵盖\ ``fpm-alpine``\ 的用法。为此，笔者在这里做了小小的总结。

笔者选用的 WordPress 镜像标签为\ ``php7.4-fpm-alpine``\ ，这个标签下的镜像是以\ ``php:7.4-fpm-alpine``\ 为基础构建出来的。

Docker Compose
==============

首先，以下面这个\ ``docker-compose.yml``\ 文件为例，运行一个 WordPress 实例。

.. code:: yaml

   version: '3.1'

   services:

     wordpress:
       image: wordpress:php7.4-fpm-alpine
       restart: always
       ports:
         - 9000:9000
       environment:
         WORDPRESS_DB_HOST: db
         WORDPRESS_DB_USER: dbuser
         WORDPRESS_DB_PASSWORD: mansworldismutable
         WORDPRESS_DB_NAME: dbname
         WORDPRESS_TABLE_PREFIX: jinkan_
       volumes:
         - /somewhere/wordpress:/var/www/html

     db:
       image: mariadb
       restart: always
       environment:
         MYSQL_DATABASE: dbname
         MYSQL_USER: dbuser
         MYSQL_PASSWORD: mansworldismutable
         MYSQL_RANDOM_ROOT_PASSWORD: seasbecomemulberryfields
       volumes:
         - db:/var/lib/mysql

   volumes:
     db:

PHP-FPM 配置
============

在运行该镜像的容器实例后，通过\ ``docker exec -ti <WordPress容器名称>/bin/sh``\ 进入容器的 Shell，查看 PHP-FPM 的配置。

在\ ``/usr/local/etc/php-fpm.conf``\ 文件的最后一行，可以看到下面这行配置。

.. code:: ini

   include=etc/php-fpm.d/*.conf

即 PHP-FPM 配置中会自动包含\ ``/usr/local/etc/php-fpm.d``\ 目录下所有以\ ``.conf``\ 结尾文件的内容。镜像中该目录下包含 3 个\ ``.conf``\ 文件：\ ``docker.conf``\ 、\ ``www.conf``\ 和\ ``zz-docker.conf``\ ，其中有两个文件需要特别关注。

一是\ ``www.conf``\ 中配置了一个名为\ ``www``\ 的 PHP-FPM 进程池，运行进程的用户和组均为\ ``www-data``\ 。用\ ``id``\ 命令可以看出，\ ``www-data``\ 的 UID 为 82。

.. code:: bash

   $ id www-data
   uid=82(www-data) gid=82(www-data) groups=82(www-data),82(www-data)

因此，如果需要修改 WordPress 中的文件，就需要按上述 UID 配置\ ``/somewhere/wordpress``\ 中的相应目录或文件的写权限。

二是\ ``zz-docker.conf``\ 中指定了\ ``www``\ 进程池监听 9000 端口，与 `Dockerfile <https://github.com/docker-library/php/blob/master/7.4/alpine3.12/fpm/Dockerfile#L239>`__ 中\ ``EXPOSE``\ 语句对应。

.. code:: ini

   [www]
   listen = 9000

那么，之后配置 Nginx 反向代理就要指向这个端口。

Nginx 配置
==========

这一步，先与大多数 LNMP 套件配置一样，通过 FastCGI 连接到 PHP-FPM，让 Nginx 作为反向代理。在 Nginx 的配置中添加一个\ ``upstream``\ 节，把 WordPress 容器的 9000 端口作为上游。

.. code:: nginx

   upstream wordpress {
       server 127.0.0.1:9000;
   }

修改\ ``server``\ 节的根目录为\ ``/somewhere/wordpress``\ 。

.. code:: nginx

   server {
       <...>
       root /somewhere/wordpress;
   }

然后在\ ``server``\ 节中做如下配置，匹配 WordPress 的 URL 重写机制，让 Nginx 直接提供静态文件，并代理 URL 以\ ``.php``\ 结尾的请求，提供给作为上游的 PHP-FPM。

::

   location / {
       try_files $uri $uri/ /index.php?$args;
   }

   location ~ \.php$ {
       fastcgi_pass wordpress;
       fastcgi_index index.php;
       include fastcgi_params;
       fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
   }

大多时候 LNMP 套件中的 PHP-FPM 和 Nginx 都安装在同一台机器上，所以都会配置 FastCGI 参数\ ``SCRIPT_FILENAME``\ 为\ ``$document_root$fastcgi_script_name``\ ，即让 PHP-FPM 以\ ``server``\ 节中配置的\ ``root``\ 为根目录。此时，以\ ``http://example.com/index.php``\ 为例，则会让作为上游的 PHP-FPM 执行\ ``/somewhere/wordpress/index.php``\ 文件，会在 Nginx 日志中得到这样的错误。

::

   2020/10/11 17:00:14 [error] 101982#101982: *17 FastCGI sent in stderr: "Primary script unknown" while reading response header from upstream, client: 42.42.42.42, server: example.com, request: "GET / HTTP/1.1", upstream: "fastcgi://127.0.0.1:9000", host: "example.com"

这是因为 WordPress 镜像中，WordPress 代码根目录实际位于\ ``/var/www/html``\ ，也是 PHP-FPM 需要访问的根目录，而镜像中\ ``/somewhere/wordpress``\ 并不存在。因此，需要修改该参数为如下。

.. code:: nginx

   location ~ \.php$ {
       <...>
       fastcgi_param SCRIPT_FILENAME /var/www/html/$fastcgi_script_name;
   }

然后，就没有然后了。
