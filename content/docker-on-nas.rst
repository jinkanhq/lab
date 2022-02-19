NAS 上的 Docker
###############
:date: 2020-05-24 20:46
:author: yinian
:category: Uncategoried
:tags: Docker, NAS
:slug: docker-on-nas
:status: published
:feature: /images/2020/bandwidth-close-up-computer-connection-1148820-docker-feature.jpg
:abstract: 用 Docker 替代原有的 Hyper-V 虚拟机，一次性解决运行环境的依赖问题的折腾笔记

前言
====

因为笔者 NAS 之前运行的 Windows Server 2019 授权过期，又恰巧 Ubuntu 20.04 LTS 发布，就把 NAS 的各种功能迁移到了 Ubuntu 中，并用 Docker 替代原有的 Hyper-V 虚拟机，一次性解决运行环境的依赖问题，体验了肉眼可见的性能提升，以下即是迁（zhe）移（teng）过程的要点笔记。

Docker
======

在 2020 年，Docker 已经不是新事物了，许多开源项目都在 Docker Hub 上发布了开箱即用的容器镜像，本文也是直接使用了现成的官方镜像运行 NAS 上的容器，并且用 Docker Compose 管理、运行这些容器。

Docker Compose 是一个能把多个容器组合成为一套应用的管理工具，它采用 YAML 格式的配置文件\ ``docker-compose.yml``\ ，代替 Docker 容器所需的冗长命令行参数。

安装与配置
----------

首先来安装 Docker Compose。Ubuntu 下的\ ``docker``\ 包是图形界面托盘\ ``wmdocker``\ 的过渡包，与容器无关。\ ``docker.io``\ 才是本尊。

.. code:: bash

   $ sudo apt install docker.io docker-compose

把当前用户添加到\ ``docker``\ 组中，就可以免去\ ``sudo``\ 直接调用\ ``docker``\ 和\ ``docker-compose``\ 了。

.. code:: bash

   $ sudo gpasswd -a $USER docker

确认安装是否成功以及安装的版本。

.. code:: bash

   $ docker -v
   Docker version 19.03.8, build afacb8b7f0
   $ docker-compose -v
   docker-compose version 1.25.0, build unknown

若要把 Docker 数据放在默认\ ``/var/lib/docker``\ 以外的位置，可以编辑\ ``/etc/docker/daemon.json``\ 加入以下内容。

.. code:: json

   {
     "data-root": "/data0/dockerlib"
   }

在\ ``daemon.json``\ 中几乎可以配置所有的\ ``dockerd``\ 选项，其中的一个例外就是代理。但由于众所周知的网络环境问题，在国内从\ Docker Hub\ 下载镜像的速度难以忍受，不得不给\ ``dockerd``\ 配置代理。

Ubuntu 中的\ ``dockerd``\ 由\ ``systemd``\ 管理，那么编辑\ ``docker.service``\ 配置。

.. code:: bash

   $ sudo systemctl edit docker

根据你的代理具体配置，在其中写入下面的内容。

.. code:: ini

   [Service]
   Environment="HTTPS_PROXY=http://host:port"
   Environment="HTTP_PROXY=http://host:port"
   Environment="NO_PROXY=localhost,127.0.0.0/8,192.168.0.0/16"

保存后，重新加载\ ``systemd``\ 配置文件，检查代理配置。

.. code:: bash

   $ sudo systemctl daemon-reload
   $ sudo systemctl show --property Environment docker
   Environment=HTTPS_PROXY=http://host:port HTTP_PROXY=http://host:port NO_PROXY...

重启\ ``dockerd``\ 让代理配置生效。

.. code:: bash

   $ sudo systemctl restart docker

Hello World
-----------

运行\ ``hello-world``\ 镜像，确认 Docker 环境配置无误。因为本地没有\ ``hello-world``\ 的镜像，Docker 会自动从 Docker Hub 中拉取。若 Docker 能正常拉取镜像并运行容器，则会输出类似下面的内容。

.. code:: bash

   $ docker run hello-world
   Unable to find image 'hello-world:latest' locally
   latest: Pulling from library/hello-world
   0e03bdcc26d7: Pull complete
   Digest: sha256:6a65f928fb91fcfbc963f7aa6d57c8eeb426ad9a20c7ee045538ef34847f44f1
   Status: Downloaded newer image for hello-world:latest

   Hello from Docker!
   This message shows that your installation appears to be working correctly.
   ...

用\ ``docker ps``\ 命令即可看到我们用\ ``hello-world``\ 镜像创建的容器，在输出内容后处于正常退出（Exited）状态。

.. code:: bash

   $ docker ps --all | grep hello-world
   25063973ebe3        hello-world            "/hello"                 28 seconds ago      Exited (0) 27 seconds ago

至此，Docker 的安装与配置就完成了，只是还没试过 Docker Compose，接下来将会给各个应用编写相应的\ ``docker-compose.yml``\ 。

NAS 应用
========

笔者为不同应用绑定了不同的域名，因此需要复用 HTTP/HTTPS 端口以及同一个 nginx 实例作为反向代理。如果在这个 nginx 实例的配置中通过主机名访问其他应用的容器，则会出现其他应用未启动容器时，无法解析容器的主机名而无法启动。为了解除这种奇怪的依赖，笔者把各个应用都映射到主机的端口，然后在主机网络（host network）运行这一 nginx 实例，反向代理各个应用的端口。

.. image:: /images/2020/network.png
   :alt: 网络结构

NextCloud
---------

笔者根据 NextCloud 官方提供的\ `样例 <https://github.com/nextcloud/docker/tree/master/.examples/docker-compose/insecure/mariadb-cron-redis/fpm>`__\ 做了一些调整。\ ``docker-compose.yml``\ 和涉及的额外文件目录结构如下。

.. code:: bash

   .
   ├── db.env
   ├── docker-compose.yml
   └── web
       ├── Dockerfile
       └── nginx.conf

   1 directory, 4 files

Compose
~~~~~~~

首先来看\ ``docker-compose.yml``\ 中定义的服务、网络、卷。

.. code:: yaml

   version: '3.7'

   services:
     db:
       image: mariadb
       command: --transaction-isolation=READ-COMMITTED --binlog-format=ROW
       restart: always
       networks:
         - nextcloud
       volumes:
         - db:/var/lib/mysql
       environment:
         - MYSQL_ROOT_PASSWORD=<root_password>
       env_file:
         - db.env

     redis:
       image: redis:alpine
       restart: always
       networks:
         - nextcloud
       volumes:
         - redis:/data

     app:
       image: nextcloud:fpm-alpine
       restart: always
       networks:
         - nextcloud
       volumes:
         - app:/var/www/html
         - data:/var/www/html/data
       environment:
         - MYSQL_HOST=db
         - REDIS_HOST=redis
       env_file:
         - db.env
       depends_on:
         - db
         - redis

     cron:
       image: nextcloud:fpm-alpine
       restart: always
       networks:
         - nextcloud
       volumes:
         - app:/var/www/html
         - data:/var/www/html/data
       entrypoint: /cron.sh
       depends_on:
         - db
         - redis

     web:
       image: nginx:nextcloud
       build: ./web
       restart: always
       networks:
         - nextcloud
       ports:
         - 10080:80
       volumes:
         - app:/var/www/html:ro

   volumes:
     db:
     redis:
     app:
     data:
       driver_opts:
         type: "none"
         o: "bind"
         device: "/host/folder"

   networks:
     nextcloud:

关键配置如下。

-  服务\ ``db``\ ：MariaDB 实例。它使用命名卷\ ``db``\ 作为 MariaDB 的默认存储位置，从\ ``db.env``\ 文件加载环境变量，并额外添加环境变量设置 MariaDB 的 root 用户密码。
-  服务\ ``redis``\ ：Alpine 中的 Redis 实例，作为 NextCloud 的缓存。它使用命名卷\ ``redis``\ 作为 redis 的默认存储位置。
-  服务\ ``app``\ ：Alpine 中的 PHP-FPM 运行的 NextCloud 实例，用环境变量指定了 MariaDB 和 Redis 的主机名。它使用命名卷\ ``app``\ 作为 NextCloud 源码根目录，命名卷\ ``data``\ 作为 NextCloud 的用户数据存储。
-  服务\ ``cron``\ ：Alpine 中的 NextCloud Cron 脚本实例。它与\ ``app``\ 复用命名卷\ ``app``\ 和\ ``data``\ 。
-  服务\ ``web``\ ：从\ ``web``\ 文件夹中的\ ``DockerFile``\ 构建自定义镜像\ ``nginx:nextcloud``\ 。以只读权限复用命名卷\ ``app``\ ，作为 PHP-FPM 的反向代理，并映射 80 端口到 Docker 主机的 10080 端口。
-  命名卷\ ``data``\ ：其参数的效果等同于\ ``mount --bind <data_volume_path> /host/folder``\ ，即把 Docker 主机中的目录作为命名卷。
-  网络\ ``nextcloud``\ ：把所有服务置于该网络中。

额外文件
~~~~~~~~

``db.env``\ 中是提供数据库连接信息的环境变量。这 3 个环境变量是 MariaDB 和 NextCloud 共用的。

::

   MYSQL_PASSWORD=<password>
   MYSQL_DATABASE=nextcloud
   MYSQL_USER=nextcloud

``web``\ 文件夹中的\ ``Dockerfile``\  中是构建镜像的指令。

.. code:: docker

   FROM nginx:stable-alpine

   COPY nginx.conf /etc/nginx/nginx.conf

此处是覆盖\ ``nginx:stable-alpine``\ 中的 ``nginx.conf``\ 。移除样例中的两处 HTTP 301 跳转。

.. code:: diff

   -        location = /.well-known/carddav {
   -            return 301 $scheme://$host:$server_port/remote.php/dav;
   -        }
   -        location = /.well-known/caldav {
   -            return 301 $scheme://$host:$server_port/remote.php/dav;
   -        }

然后把这两处 HTTP 301 跳转写入主机网络反向代理 nginx 的配置文件中。

Gitea
-----

Gitea 的配置就比较简单，除 Gitea 本身之外只需再配置一个 MariaDB 实例。

.. code:: yaml

   version: "3.7"

   services:
     app:
       image: gitea/gitea:latest
       environment:
         - DB_TYPE=mysql
         - DB_HOST=db
         - DB_NAME=gitea
         - DB_USER=gitea
         - DB_PASSWD=<password>
         - DOMAIN=git.example.com
         - SSH_DOMAIN=git.example.com
       restart: always
       networks:
         - gitea
       volumes:
         - app:/data
         - /etc/timezone:/etc/timezone:ro
         - /etc/localtime:/etc/localtime:ro
       ports:
          - 10030:3000
          - 22:22
       depends_on:
         - db

     db:
       image: mariadb
       restart: always
       environment:
         - MYSQL_ROOT_PASSWORD=<root_password>
         - MYSQL_USER=gitea
         - MYSQL_PASSWORD=<password>
         - MYSQL_DATABASE=gitea
       networks:
         - gitea
       volumes:
         - db:/var/lib/mysql

   volumes:
     db:
     app:

   networks:
     gitea:

为了直接把 Docker 主机的 SSH 端口（22）映射给 Gitea 使用，需要修改 Docker 主机的\ ``sshd``\ 配置，防止端口冲突。

以 10022 端口为例，修改\ ``/etc/ssh/sshd_config``\ ，注释掉默认的 22 端口，添加 10022 端口。如果启用了防火墙，还需要添加相应规则放行 10022 端口。

::

   #Port 22
   Port 10022

之后重启\ ``sshd``\ 。

::

   $ systemctl restart sshd

nginx 反向代理
--------------

这个 nginx 实例反向代理其他应用，提供 HTTPS 加密。

::

   .
   ├── docker-compose.yml
   └── proxy
       ├── certs
       │   ├── 1_git.example.com_bundle.crt
       │   ├── 1_nextcloud.example.com_bundle.crt
       │   ├── 2_git.example.com.key
       │   └── 2_nextcloud.example.com.key
       ├── Dockerfile
       └── nginx.conf

   2 directories, 7 files

这里通过构建自定义镜像，把相应域名的 SSL 证书和\ ``nginx.conf``\ 打包到镜像中。

.. code:: docker

   FROM nginx:stable-alpine

   COPY nginx.conf /etc/nginx/nginx.conf
   COPY certs/1_nextcloud.example.com_bundle.crt /etc/nginx/nextcloud_bundle.crt
   COPY certs/2_nextcloud.example.com.key /etc/nginx/nextcloud_private.key
   COPY certs/1_git.example.com.crt /etc/nginx/git_bundle.crt
   COPY certs/2_git.example.com.key /etc/nginx/git_private.key

此处的\ ``docker-compose.yaml``\  只定义了服务，且直接使用了 Docker 主机（host）网络。

.. code:: yaml

   version: '3.7'

   services:
     nginx:
       image: nginx:kaguya
       build: ./proxy
       restart: always
       network_mode: host
       ports:
         - 80:80
         - 443:443

在默认的\ ``nginx.conf``\ 文件\ ``http``\ 块中为每个应用添加类似下面的\ ``server``\ 块。下面的配置以 NextCloud 为例。

.. code:: nginx

   server {
       listen 80;
       server_name nextcloud.example.com;
       return 301 https://$server_name$request_uri;
   }

   server {
       listen 443 ssl http2;
       server_name nextcloud.example.com;
       ssl_certificate /etc/nginx/nextcloud_bundle.crt;
       ssl_certificate_key /etc/nginx/nextcloud_private.key;
       ssl_session_cache shared:SSL:20m;
       ssl_session_timeout 10m;
       ssl_protocols TLSv1.2;
       ssl_prefer_server_ciphers on;
       ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256';

       client_max_body_size 10G;

       location = /.well-known/carddav {
           return 301 $scheme://$host:$server_port/remote.php/dav;
       }

       location = /.well-known/caldav {
           return 301 $scheme://$host:$server_port/remote.php/dav;
       }

       location / {
           proxy_pass http://127.0.0.1:10080;
       }
   }

关键配置如下：

-  把前面移除的几行 HTTP 301 跳转加入到\ ``server``\ 块中。
-  设置\ ``client_max_body_size``\ ，使其与 NextCloud 应用中的\ ``web``\ 配置一致。

管理应用状态
------------

分别进入各个应用\ ``docker-compose.yml``\ 所在的目录创建并启动相应的容器。下面以 NextCloud 为例。

.. code:: bash

   $ cd nextcloud
   $ docker-compose up

或者也可以手动指定\ ``docker-compose.yml``\ 。

.. code:: bash

   $ docker-compose -f /data0/apps/nginx/docker-compose.yml up

之后可以用\ ``ps``\ 查看容器运行状态。

.. code:: bash

   $ docker-compose ps
         Name                     Command               State           Ports
   ----------------------------------------------------------------------------------
   nextcloud_app_1     /entrypoint.sh php-fpm           Up      9000/tcp
   nextcloud_cron_1    /cron.sh                         Up      9000/tcp
   nextcloud_db_1      docker-entrypoint.sh --tra ...   Up      3306/tcp
   nextcloud_redis_1   docker-entrypoint.sh redis ...   Up      6379/tcp
   nextcloud_web_1     nginx -g daemon off;             Up      0.0.0.0:10080->80/tcp

除了\ ``up``\ 以外，还有许多其他的命令。

-  ``down``\ ：与\ ``up``\ 相对，停止并移除容器和网络。
-  ``build``\ ：重新构建指定服务的镜像。
-  ``start``\ ：启动指定服务。
-  ``stop``\ ：停止指定服务。
-  ``rm``\ ：移除已停止服务的容器。

执行\ ``docker-compose help``\ 或\ ``docker-compose help <command>``\ 可以查看更多命令以及更多额外参数的用法。

至此，大功告成！
