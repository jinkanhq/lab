OpenLDAP 从零开始：（一）TLS 配置
############################################
:date: 2022-09-15 12:50
:author: yinian
:category: Uncategoried
:tags: OpenLDAP, LDAP
:slug: openldap-from-scratch-1
:status: published
:feature: /images/2022/pexels-anton-atanasov-226721.jpg
:abstract: 从零开始编译安装 OpenLDAP，记录一些配置与最佳实践

.. role:: strike
   :class: strike

前言
=======

在上一章中，我们从源码编译了 OpenLDAP 套件中的 slapd，并启用了 Argon2 支持。密\
码的存储似乎已经安全了，但客户端与服务器之间传输仍是明文的、不可靠的，存在中\
间人攻击的风险。本章中将在 slapd 中启用 TLS 配置，以保护 LDAP 连接。

如果已有根证书颁发机构的部署或已有常见根证书颁发机构（如 Let's Encrypt）签发的\
证书，可以跳过第 2 节的内容。

.. attention::

  本文中涉及的部分命令需要以 root 身份运行。

1. 传输层安全协议
====================

**TLS** 是传输层安全协议（Transport Layer Security），也经常与其前身安全套接\
层（SSL，Secure Sockets Layer）的并列，写作 TLS/SSL。有时也直接以 SSL 代之。该\
协议广泛应用于电子邮件、即时通信等应用中，最常见的场景就是 HTTPS。SSL 系列协议\
由于年代久远且屡屡爆出安全隐患问题，自 2015 年后已被全面弃用。

TLS 协议旨在运用证书来提供加密，保护端对端的通信秘密、完整和认证功能，免受第三\
方的窥探和篡改。TLS 在 1999 年被互联网工程任务组（IETF，Internet Engineering
Task Force）确立为标准之一。目前最新的 TLS 版本为 1.3，为同时兼顾安全性和兼容\
性，本文遵循 `Mozilla SSL 配置生成器 <https://ssl-config.mozilla.org/>`_\ ，采
用同时启用 TLS 1.2 和 TLS 1.3 的中间（Intermediate）配置。

2. 签发证书
================

这一节将以 OpenSSL 命令行工具为例，签发根证书和服务器证书。首先为根证书编写OpenSSL 配置文件。

.. code-block:: ini

  [ req ]
  distinguished_name  = req_distinguished_name
  string_mask         = utf8only
  x509_extensions     = v3_ca
  prompt              = no

  [ req_distinguished_name ]
  countryName                     = CN
  stateOrProvinceName             = Beijing
  localityName                    = Beijing
  organizationName                = Jinkan
  organizationalUnitName          = Jinkan
  commonName                      = Jinkan Certificate Authority
  emailAddress                    = admin@jinkan.org

  [ v3_ca ]
  subjectKeyIdentifier = hash
  authorityKeyIdentifier = keyid:always,issuer
  basicConstraints = critical, CA:true
  keyUsage = critical, digitalSignature


把这段内容保存为 ``ca.conf`` 文件，然后执行如下命令，生成根证书的 4096 位 RSA
私钥，并签发\ :strike:`可以窖藏`\ 20 年的根证书。

.. code-block:: console

  $ openssl genrsa -out ca.key 4096
  $ openssl req -x509 -new -sha512 -nodes -key ca.key -days 7307 -out ca.crt -config ca.conf

接下来给服务器证书编写 OpenSSL 配置。此处要注意 ``commonName`` 和 ``sans`` 部分\
应与服务器的主机名一致。

.. code-block:: ini

  [ req ]
  prompt              = no
  days                = 365
  default_md          = sha256
  distinguished_name  = req_distinguished_name
  req_extensions      = v3_req

  [ req_distinguished_name ]
  countryName                     = CN
  stateOrProvinceName             = Beijing
  localityName                    = Beijing
  organizationName                = Jinkan
  organizationalUnitName          = Jinkan
  commonName                      = ldap.jinkan.org
  emailAddress                    = admin@jinkan.org

  [ v3_req ]
  basicConstraints = CA:false
  subjectKeyIdentifier = hash
  authorityKeyIdentifier = keyid,issuer:always
  keyUsage = critical, digitalSignature, keyEncipherment
  extendedKeyUsage = serverAuth
  subjectAltName = @sans

  [ sans ]
  DNS.0 = ldap.jinkan.org

保存为 ``server.conf`` 文件后，执行如下命令，先签发服务器证书请求，再用根证书\
签发服务器证书。

.. code-block:: console

  $ openssl req -config server.conf -key server.key -new -out server.csr
  $ openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -out server.crt \
    -extfile server.conf -extensions v3_req

用根证书验证服务器证书是否有效。

.. code-block:: console 

  $ openssl verify -CAfile ca.crt server.crt
  server.crt: OK

如此，根证书和服务器证书就都签发成功了。给 ``server.key`` 设置适当的权限以保护私钥。

.. code-block:: console

  # chown root:root server.key
  # chmod 400 server.key

3. 已有证书
================

首先，确认系统中是否安装了常见的根证书。

.. code-block:: console

    $ ls /etc/ssl/certs/ca-certificates.crt

如果没有，可以通过包管理器安装。

.. code-block:: console

    $ sudo apt install ca-certificates

之后，只需准备好服务器证书和私钥。

4. 配置 TLS
=====================

这一节仍然需要编写 LDIF 文件，但与初始化时不同，此时已经有配置数据库实例了，不\
能继续使用 ``slapadd`` 工具，应换用 ``slapmodify`` 工具，为 ``cn=config`` 添加\
属性（Attribute）。

4.1 证书
-----------

编写如下 LDIF 文件，分别添加 ``olcTLSCACertificateFile``\ 、\ 
``olcTLSCertificateFile`` 和 ``olcTLSCertificateKeyFile`` 属性，对应 CA 证书文
件、服务器证书文件、服务器私钥文件。

.. code-block:: text

  dn: cn=config
  changetype: modify
  add: olcTLSCACertificateFile
  olcTLSCACertificateFile: /path/to/ca.crt
  -
  add: olcTLSCertificateFile
  olcTLSCertificateFile: /path/to/server.crt
  -
  add: olcTLSCertificateKeyFile
  olcTLSCertificateKeyFile: /path/to/server.key

该 LDIF 文件中 ``changetype: modify`` 意为修改 DN 为 ``cn=config`` 的条\
目（Entry）属性，修改方式为添加（add）属性，随后是要添加的属性值，各个属性修\
改以仅有 ``-`` 的行分隔。

这里先保存到 ``tls.ldif`` ，后面用 ``slapmodify`` 工具使其生效。

4.2 TLS 参数
----------------

首先，用 ``olcTLSCipherSuite`` 指定密码套件。由于编译时 SSL 依赖选用了
OpenSSL，那么此处填写的密码套件也是 OpenSSL 格式的。向 ``tls.ldif`` 中添加下面\
的内容。

.. code-block:: text

  -
  add: olcTLSCipherSuite
  olcTLSCipherSuite: ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384

这些密码套件中都使用了短暂迪菲-赫尔曼密钥交换（DHE，Diffie-Hellman Key
Exchange）和短暂椭圆曲线迪菲-赫尔曼密钥交换（ECDHE，Elliptic Curve
Diffie-Hellman Key Exchange），能提供完全向前保密（PFS，Perfect Forward
Secrecy），即便私钥暴露，攻击者也不能解密暴露之前的会话内容。

为此，需要用 ``olcTLSDHParamFile`` 指定 DH 参数。因为服务器私钥为 2048 位，也\
要选择相同位数的 DH 参数。最好是从 Mozilla 下载这个参数，不建议自行生成。

.. code-block:: console

  $ wget https://ssl-config.mozilla.org/ffdhe2048.txt

把下面这段添加到 ``tls.ldif`` 中。

.. code-block:: text

  -
  add: olcTLSDHParamFile
  olcTLSDHParamFile: /path/to/server.key

之后运行 ``slapmodify`` 使 TLS 参数生效。

.. code-block:: console

  # slapmodify -n 0 -F /usr/local/etc/slapd.d -l certs.ldif

与 ``slapadd`` 相同，\ ``-n`` 参数指定数据库序号。此处需要修改配置数据库中的内\
容，则指定为 0。

5. 配置安全强度系数
======================

OpenLDAP 中的\ **安全强度系数**\ （SSF，Security Strength Factor）用于控制特定\
操作的密钥强度下限。在 ``olcSecurity`` 中可以配置一组系数，控制不同的操作。

下面列出了几种常见的安全强度系数。

* ``ssf``\ ：全局安全强度系数。
* ``tls``\ ：TLS 安全强度系数。
* ``update_ssf``\ ：更改内容所需的安全强度系数。
* ``simple_bind``\ ：简单认证（即用户名/密码认证）所需的安全强度系数。

简单起见，本文直接配置了与密码套件对应的全局安全强度系数，全局禁用了明文操作。

.. code-block:: text

  dn: cn=config
  changetype: modify
  add: olcSecurity
  olcSecurity: ssf=128

将这段文本保存至 ``ssf.ldif``\ ，用 ``slapdmodify`` 工具使其生效。

6. 测试 TLS 配置
=====================

首先启动 sladp，不指定 ``-d`` 参数，让它运行在后台。

.. code-block:: console

  # slapd -F /usr/local/etc/slapd.d

.. note::

  当不指定 ``-h`` 参数运行 slapd 时，默认端点为 ``ldap:///``\ ，即监听所有网络\
  接口上的 LDAP 标准端口 389，并支持 StartTLS。

  虽然 slapd 支持监听 ``ldaps:///`` 端点，即在 TLS 中传输 LDAP 协议，默认端口\
  为 636。这种方式不是 LDAP 标准中定义的，端口号也不是互联网工程指导小\
  组（IESG，Internet Engineering Steering Group）注册的，因此不推荐使用。\
  [IANA-PORT]_

可以尝试用客户端工具 ``ldapsearch`` 以简单绑定（Simple Bind）方式明文连接服务\
器。命令中的参数意义如下。

* ``-x``\ ：使用简单认证。
* ``-h``\ ：服务器主机名。
* ``-D``\ ：要绑定的 DN。
* ``-W``\ ：提示输入绑定密码。

.. code-block:: console

  $ ldapsearch -x -h ldap.jinkan.org -D 'cn=admin,dc=jinkan,dc=org' -W
  Enter LDAP Password: 
  ldap_bind: Confidentiality required (13)
          additional info: confidentiality required

返回状态码为 13，服务器拒绝了明文连接，并要求使用加密连接。可以看出安全强度系\
数起效果了。

增加 ``-ZZ`` 参数，使用 TLS 向服务器发起请求，并在发起 TLS 连接失败的情况下退\
出。

.. code-block:: console

  $ ldapsearch -x -h ldap.jinkan.org -D 'cn=admin,dc=jinkan,dc=org' -W -ZZ
  Enter LDAP Password: 

可以看到成功用 TLS 连接到服务器，并返回了查询结果，只不过结果为空。

.. code-block:: text

  # extended LDIF
  #
  # LDAPv3
  # base <> (default) with scope subtree
  # filter: (objectclass=*)
  # requesting: ALL
  #

  # search result
  search: 3
  result: 32 No such object

  # numResponses: 1

若出现如下报错提示，可能是由于服务器证书的通用名（Common Name）字段是否与主机\
名不一致，请检查主机名和服务器证书。

.. code-block:: text

  ldap_start_tls: Connect error (-11)
          additional info: (unknown error code)

7. 小结
=============

本章遵循当前 TLS 最佳实践，启用了 TLS 1.2 和 TLS 1.3 并行的配置，为 slapd 配置\
了服务器证书和 TLS 参数，并设置了安全强度系数，要求客户端通过指定强度以上的
TLS 访问。

迄今为止，我们只是试验性运行了 slapd，目录服务中仍没有实际的内容。下一章将开始\
向目录服务插入条目，启用覆盖（Overlay），试验一些动态特性。

.. raw:: html

    <div class="divider"><div class="inner-text">引用</div></div>

.. [IANA-PORT] `Service Name and Transport Protocol Port Number Registry
   <https://www.iana.org/assignments/service-names-port-numbers/
   service-names-port-numbers.xhtml?search=636>`_
