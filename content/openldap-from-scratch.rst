OpenLDAP 从零开始：（零）编译安装与初始化
############################################
:date: 2022-09-10 17:33
:author: yinian
:category: Uncategoried
:tags: OpenLDAP, LDAP
:slug: openldap-from-scratch
:status: published
:feature: /images/2022/pexels-veeterzy-38136.jpg
:abstract: 从零开始编译安装 OpenLDAP，记录一些配置与最佳实践

.. role:: strike
   :class: strike rainbow-animated

前言
==========

OpenLDAP 是一个由社区主导的开源 LDAP 套件项目，可作为 Microsoft Active
Directory 等商业 LDAP 服务器的替代。OpenLDAP 套件包含独立 LDAP 服务\
器（slapd）、配套的负载均衡器（llopd）、LDAP 协议库（libldap 等）。本文将从零\
开始，从源码编译 OpenLDAP 套件中的 slapd，搭建一个安全可靠的 LDAP 服务。

OpenLDAP 项目维护有两个主要发布版本：

* 特性优先发布版本（Feature Release）
* 长期支持发布版本（Long Term Support Release）

本文中将以特性优先发布版本为例，在 Debian 11 Bullseye 上，从源码构建 slapd。

.. attention::

  本文中涉及的部分命令需要以 root 身份运行。

1. 获取源码
==============

本文形成时，特性优先发布版本的最新版本号为 2.6.3，那么以此版本为例，设置如下环\
境变量。

.. code-block:: console

  $ export OPENLDAP_VERSION=2.6.3

接下来，从 OpenLDAP 官网下载相应版本的源码包和数字签名。

.. code-block:: console

  $ wget https://www.openldap.org/software/download/OpenLDAP/openldap-release/openldap-${OPENLDAP_VERSION}.tgz
  $ wget https://www.openldap.org/software/download/OpenLDAP/openldap-release/openldap-${OPENLDAP_VERSION}.tgz.asc

从公钥服务器获取 OpenLDAP 项目的公钥，并验证源码包的完整性。

.. code-block:: console

  $ gpg --keyserver keyserver.ubuntu.com --recv 7F67D5FD1CE1CBCE
  $ gpg --verify openldap-${OPENLDAP_VERSION}.tgz.asc

确认源码包完整性无误后，便可解压源码包。

.. code-block:: console

  $ tar xf openldap-${OPENLDAP_VERSION}.tgz

在编译开始之前，还需要一点准备工作，即配置编译参数。

2. 编译参数与依赖
=========================

进入源码目录后，以 ``--help`` 参数运行 ``configure``\ ，查看 OpenLDAP 的编译参\
数。

.. code-block:: console

  $ ./configure --help
  `configure' configures this package to adapt to many kinds of systems.

  Usage: ./configure [OPTION]... [VAR=VALUE]...

  To assign environment variables (e.g., CC, CFLAGS...), specify them as
  VAR=VALUE.  See below for descriptions of some of the useful variables.

  Defaults for the options are specified in brackets.

  Configuration:
  -h, --help              display this help and exit
      --help=short        display options specific to this package
      --help=recursive    display the short help of all the included packages
  -V, --version           display version information and exit
  -q, --quiet, --silent   do not print `checking ...' messages
      --cache-file=FILE   cache test results in FILE [disabled]
  -C, --config-cache      alias for `--cache-file=config.cache'
  -n, --no-create         do not create output files
      --srcdir=DIR        find the sources in DIR [configure dir or `..']
  ...

可以看到相当多的编译参数，分成下面几类。

* 安装目录
* 系统类型
* 可选特性
* slapd 选项
* slapd 覆盖（Overlay）选项，默认不编译任何覆盖
* slapd 后端（Backend）选项，默认包含 mdb 后端
* slapd 密码模块选项，仅支持 argon2
* llopd 选项
* 库生成与链接选项
* 可选包

本文的安装方式仅启用了如下参数。

* ``--enable-wrappers``\ ：启用 TCP 包装（Wrapper）功能，以支持设置 IP 级别的访\
  问控制。运行时依赖于 ``libwrap0`` 包，编译时依赖于 ``libwrap0-dev`` 包。
* ``--enable-modules``\ ：支持动态加载模块，运行时依赖于 ``libltdl7`` 包，编译\
  时依赖于 ``liblttdl-dev``\ 。
* ``--enable-overlays=mod``\ ：启用覆盖支持，且编译成模块，可在配置中动态加载。
* ``--enable-crypt``\ ：启用 Linux 系统 ``crypt(3)`` 散列函数密码模式支持。运行\
  时依赖于 ``libcrypt1`` 包，编译时依赖于 ``libcrypt-dev`` 包。
* ``--enable-argon2``\ ：启用 Argon2 密码模式支持。运行时依赖于 ``libsodium23``\
  包，编译时依赖于 ``libsodium-dev`` 包。

除此之外，为了可以使用 TLS 连接，还依赖于 OpenSSL，编译时依赖于
``libssl-dev``\ 。线程支持还需要编译时依赖 ``libevent-dev``\ 。

那么首先要从软件源安装这些依赖和编译必需的工具集。

.. code-block:: console

  $ sudo apt-get update
  $ sudo apt-get install -y libssl-dev libwrap0 libwrap0-dev \
    libcrypt1 libcrypt-dev libsodium23 libsodium-dev \
    libltdl7 libltdl-dev libevent-dev build-essential groff-base

然后配置编译参数。

.. code-block:: console

  $ ./configure --enable-wrappers --enable-modules --enable-overlays=mod \
  --enable-crypt --enable-argon2

确认没有报错后，开始编译依赖和 slapd 本体。

.. code-block:: console

  $ make depend
  $ make
  $ sudo make install

因为本文中没有配置安装目录相关的参数，将会安装至默认的目录，具体目录如下所示。

* slapd 主程序位于 ``/usr/local/libexec``\ 。
* 样例配置文件位于 ``/usr/local/etc``\ 。
* 覆盖、模块位于 ``/usr/local/libexec/openldap``\ 。
* slapd 离线配置工具位于 ``/usr/local/sbin``\ 。
* LDAP 库位于 ``/usr/local/lib``\ 。
* LDAP 客户端工具位于 ``/usr/local/bin``\ 。

确认安装无误后，即可根据上述目录，导出相应的环境变量，方便后续的配置及运行。

.. code-block:: console

  # export LD_LIBRARY_PATH=/usr/local/lib:/usr/local/libexec/openldap
  # export PATH=$PATH:/usr/local/sbin:/usr/local/libexec

下一节中，将用 slapd 离线配置工具生成一套配置，距离安全可靠的 LDAP 服务又近了\
一步。

3. 基础配置
===================

自 OpenLDAP 2.3 以后的版本中，采用了运行时的动态配置，配置修改即时生效，不需要\
重启 slapd 进程。动态配置是完全适配 LDAP 的，可以用标准的 LDAP 操作来管理，并\
存储在 LDIF 数据库中。默认情况下，这个数据库位于
``/usr/local/etc/openldap/slapd.d``\ 。

.. image:: /images/2022/openldap-config.png

.. note::

  **COSINE** 是欧洲开放系统互联网络合作组织（Cooperation for Open Systems
  Interconnection Networking in Europe）的缩写。该组织旨在建立一个全欧洲\
  的、遵循 OSI 标准的计算机网络基础设施，用于研究、开发人员的相互交流。它是\
  由欧洲研究联合网络（RARE，Réseaux Associés pour la Recherche
  Européenne）在 1988 年秋季着手制订规范，在 1989 年启动实施的一个项目。

OpenLDAP 的配置树的结构如上图所示。配置树的根节点是 ``cn=config``，用于存放全局\
配置。其他的配置作为它的子节点，包括下面几种。

* 动态加载的模块 ``cn=module{0},cn=config``\ 。在上一节中，编译时使用了
  ``--enable-modules`` 参数，因此可以使用此功能。
* LDIF 模式定义 ``cn=schema,cn=config``\ 。
* 指定后端的配置。
* 指定数据库的配置。\ ``olcDatabase={1}mdb,cn=config`` 即是序号为 1 的 mdb 后端
  数据库配置。在数据库配置中添加覆盖配置的子节点，即可启用覆盖。不同的数据库和\
  覆盖还可以有其他的子节点。

本文采用了离线方法，也就是在未启动 slapd 时，用 ``slap*`` 前缀的工具创建、修改\
动态配置。在线方法同理，只需要换用 ``ldap*`` 前缀的工具，并采用相应的认证方式。\
两种方法都需要手动编写 LDIF 文件。

3.1 全局配置
---------------

首先从全局配置开始。

.. code-block:: text

  dn: cn=config
  objectClass: olcGlobal
  cn: config
  olcArgsFile: /usr/local/var/run/slapd.args
  olcPidFile: /usr/local/var/run/slapd.pid

这段 LDIF 文件创建了 OpenLDAP 中的 ``config`` 特殊数据库，并配置了 slapd 的运行\
参数文件和 PID 文件的位置。接下来是配置模块加载。

3.2 模块
------------

.. code-block:: text

  dn: cn=module,cn=config
  objectClass: olcModuleList
  cn: module
  olcModulepath: /usr/local/libexec/openldap
  olcModuleload: argon2.la

这段 LDIF 文件向动态配置中添加了一个模块列表，并设置模块目录为
``/usr/local/libexec/openldap``\ 。

3.3 LDIF 模式
----------------

.. code-block:: text

  dn: cn=schema,cn=config
  objectClass: olcSchemaConfig
  cn: schema

  include: file:///usr/local/etc/openldap/schema/core.ldif
  include: file:///usr/local/etc/openldap/schema/cosine.ldif
  include: file:///usr/local/etc/openldap/schema/inetorgperson.ldif

这段配置了启动时加载的一组 LDIF 模式，包含以下四种由 OpenLDAP 预置的模式。

* ``core.ldif``\ ：OpenLDAP 核心模式，包含了 RFC 2252/2256 中定义的 LDAPv3 模式\
  和 RFC 1274、RFC 2079、RFC 2247、RFC 2587、RFC 2589、RFC 2377 等标准中挑选的\
  属性和模式。
* ``cosine.ldif``\ ：COSINE 样板模式。
* ``inetorgperson.ldif``\ : RFC 2798 定义的 ``inetOrgPerson``\ ，用于表示互联网\
  或内部网络中的自然人用户。

3.4 “前端”数据库
-------------------

.. code-block:: text
   :caption: slapd.ldif 第 4 段

  dn: olcDatabase=frontend,cn=config
  objectClass: olcDatabaseConfig
  objectClass: olcFrontendConfig
  olcDatabase: frontend

这段创建了 OpenLDAP 中的一个特殊的数据库——\ ``frontend``\ 。\ ``frontend``
数据库中的设置，会成为默认的数据库级配置，在其他数据库上的配置可以覆盖这些默认\
配置。一般可以在此配置默认的访问控制，比如配置默认只读
``olcAccess: to * by * read``\ 。

3.5 mdb 后端数据库
-------------------------

OpenLDAP 中的 mdb 后端本名为\ :strike:`终极爆闪`\ 闪电内存映射数据库（Lightning
Memory-Mapped Database），是一个支持事务的、键值型的、嵌入式数据库，被设计作为\
伯克利数据库（BDB，Berkeley DB）的替代。

.. code-block:: text

  dn: olcDatabase=mdb,cn=config
  objectClass: olcDatabaseConfig
  objectClass: olcMdbConfig
  olcDatabase: mdb
  olcDbMaxSize: 1073741824
  olcSuffix: jinkan.org
  olcRootDN: cn=admin,dc=jinkan,org
  olcRootPW: {ARGON2}$argon2id$v=19$m=65536,t=2,p=1$7DPdvdN9yDuxc9CuZe2yhQ$XJsHO9r4RTRNUj6mvJ7wEqgRZFZPrB5cXPjJC841fQs
  olcDbDirectory: /usr/local/var/openldap-data
  olcDbIndex: default eq
  olcDbIndex: objectClass
  olcDbIndex: uid
  olcDbIndex: cn,sn,givenName,displayName eq,sub
  olcAccess: to attrs=userPassword
    by self write
    by anonymous auth
    by * none
  olcAccess: to *
    by self write
    by * read

这段用于建立一个 mdb 后端的数据库实例。其中 ``olcSuffix`` 指定该数据库的 DN 后\
缀，\ ``olcRootDN`` 和 ``olcRootPW`` 分别指定超级用户的 DN 和密码。这里使用
Argon2 作为密钥派生函数，由 slappasswd 命令生成。

.. code-block:: console

  # slappasswd -o module-load=argon2 -h {ARGON2} -s <secret>

因为编译时选用了 libsodium，slappasswd 将默认使用 Argon2id，内存 64 KB，迭\
代 2 次，并行度为 1，盐值长度 16 字节。详情见源码 [openldap-argon2-L45]_\ 。

.. note::

  **Argon2** 是一个密钥派生函数，是
  2015 年\ `密码散列竞赛 <https://password-hashing.net>`_\ （Password
  Hashing Competition）的优胜者，由卢森堡大学的亚历山大·比留科夫（Alex
  Biryukov）、丹尼尔·迪努（Daniel Dinu）和德米特里·霍夫拉托维奇（Dmitry
  Khovratovich）设计。它有三个变体版本。

  * Argon2d 能最大程度抵抗 GPU 穷举攻击，抗时空平衡算法，但引入了边信道攻击的\
    可能。
  * Argon2i 可以防范边信道攻击。
  * Argon2id 是混合版本，也是 RFC 9106 推荐的版本。

之后是 mdb 后端的配置。\ ``olcDbDirectory`` 指定该 mdb 实例的数据目录。\ ``olcDbIndex`` 为制定属性（Attribute）建立索引，例如
``olcDbIndex: objectClass eq`` 即为 ``objectClass`` 建立 ``eq`` 类型索引。

OpenLDAP 中的索引类型有如下四种，对应一些 LDAP 协议规范中的匹配规\
则（Matching Rule）对应。

* ``pres``\ ：存在（Presence）索引，对应存在（present）过滤选项，即查询中的
  ``(attribute=*)``\ ，检查属性是否有值。
* ``eq``\ ：相等（Equality）索引，对应相等匹配（equalityMatch）过滤选项，即查询\
  中的 ``(attribute=foo)``\ ，检查属性是否与 ``foo`` 相等。
* ``approx``\ ：近似（Approximate）索引，对应近似匹配（approxMatch）过滤选\
  项，即查询中的 ``(attribute~=foo)``\ ，检查属性是否在拼写、发音上与 ``foo`` 近\
  似。
* ``sub``\ ：子串（Substrings）索引，对应（substrings）过滤选项，即查询中的\
  通配符条件 ``(attribute=*foo*)``\ ，检查 ``foo`` 是否是属性的子串。

.. note::

  与关系数据库中的情况一样，是否建立索引和选择索引类型需要考虑到实际应用中的\
  查询条件。几乎没有应用在查询中使用（present）过滤选项，因此绝大多数情况下\
  存在索引只会带来性能负担。

这里用 ``olcDbIndex: default eq`` 配置了默认索引类型（指定了索引属性，而未指定\
索引类型时采用）为 ``eq``\ 。\ ``objectClass`` 和 ``uid`` 继承了默认索引类型。

然后是访问控制。设置用户密码属性 ``userPassword`` 仅允许用于匿名用户认证\
和用户自己读写。设置其他项为用户自己读写和其他人只读。

3.6 初始化
-----------------

把这几个部分的内容保存为 ``slapd.ldif`` 文件，创建配置中涉及的目录，设置权\
限保护配置和数据，再用 ``slapadd`` 命令使其生效。注意这里必需指定参数 ``-n 0``\ ，意为数据库序号（dbnum）为 0。

.. code-block:: console

  # mkdir -p /usr/local/etc/slapd.d
  # mkdir -p /usr/local/var/openldap-data
  # mkdir -p /usr/local/var/run
  # chmod 700 /usr/local/etc/slapd.d
  # chmod 700 /usr/local/var/openldap-data
  # slapadd -n 0 -F /usr/local/etc/slapd.d -l slapd.ldif

运行成功后，可以在 slapd 的配置目录找到这些内容。

.. code-block:: console

  # sudo ls /usr/local/etc/slapd.d
  'cn=config' 'cn=config.ldif'
  # sudo ls /usr/local/etc/slapd.d
  'cn=module{0}.ldif'  'cn=schema'  'cn=schema.ldif'  'olcDatabase={-1}frontend.ldif'  'olcDatabase={0}config.ldif'  'olcDatabase={1}mdb.ldif'

可以看到，slapd 给 3 个数据库分配了默认的序号。“前端”数据库 为 -1，配置数据库为
0，mdb 后端数据库实例为 1。这个序号可用于 ``slapadd`` 等命令的 ``-n`` 参数。

现在，运行 slapd 试一下。这里指定 ``-d`` 参数的值为 ``stats``\ ，以在终端显示\
统计信息，让 slapd 运行在前台。

.. code-block:: console

  # slapd -F /usr/local/etc/slapd.d -d stats
  31c53c9.11c26c61 0x7f803e1d2740 @(#) $OpenLDAP: slapd 2.6.3 (Sep  7 2022 02:36:18) $
    @1aed5eb8f5e2:/src/servers/slapd
  631c53c9.1c9bfcda 0x7f803e1d2740 slapd starting

4. 小结
=============

至此，就成功从源码编译安装了 OpenLDAP 服务器和客户端，并初始化了基础配置和数据\
库实例，让 slapd 成功运行起来。在下一章中，将介绍如何开启 TLS 保护 LDAP 连接免\
遭中间人攻击。

`点击此处 </files/2022/slapd.ldif>`_\ 可以下载本章中的配置文件
``slapd.ldif``\ 。


.. raw:: html

    <div class="divider"><div class="inner-text">引用</div></div>

.. [openldap-argon2-L45] openldap/openldap: `Line 45 of argon2.c <https://
   github.com/openldap/openldap/blob/788e9592bafcf1696390d5155498b152c1d14ff8/
   servers/slapd/pwmods/argon2.c#L45>`_
