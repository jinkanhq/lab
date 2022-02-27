GnuPG密钥生成三步走
###################
:date: 2020-04-30 22:14
:author: yinian
:category: Uncategoried
:tags: GnuPG, 加密, 密钥
:slug: gnupg-in-three-steps
:status: published
:feature: /images/2020/1280px-Gnupg_logo.svg-1024x420.png
:abstract: 简单介绍 GnuPG 的操作流程，给出了一种较为安全的密钥管理方法

GnuPG 简介
===========

GnuPG 是 GNU Privacy Guard 的缩写，它是一个完全开源自由的 OpenPGP 标准（由 RFC4880 定义）实现。它能加密、签名数据和通信内容，并提供了一套完整且通用的密钥管理系统，以及访问各类公钥目录的访问模块。其中的命令行工具\ ``gpg``\ 能帮你把GnuPG的功能集成到其他应用中。GnuPG 的生态丰富多样，各种平台都有前端应用和库，并且还支持 S/MIME 和 SSH 协议。

安装
====

**Windows用户**

建议下载 Gpg4win：\ https://www.gpg4win.org/

下载后注意校验安装文件完整性，具体步骤参照\ `官网说明 <https://www.gpg4win.org/package-integrity.html>`__\ 。

**Linux用户**

建议使用发行版自带的\ ``gpg``\ 命令，如果版本低于 2.2，可在访问\ `官网下载页面 <https://gnupg.org/download/index.html>`__\ 下载最新版本。

同样，下载后也需要校验安装文件的完整性，具体步骤参照\ `官网说明 <https://gnupg.org/download/integrity_check.html>`__\ 。

密钥生成
========

我们的只有三个步骤：

-  第一步，生成足够强度的主密钥，仅用于签发子密钥；
-  第二步，根据功能不同，添加独立的子密钥；
-  第三步，离线备份主密钥的私钥和吊销证书，把公钥发布到密钥服务器。

第一步：生成主密钥
------------------

在命令行中运行下面的命令，其中\ ``--full-gen-key``\ 是\ ``--full-generate-key``\ 参数的简写，允许你手动调整生成密钥对的选项，而不是像\ ``--generate-key``\ 参数采取 GnuPG 的默认值。\ ``--expert``\ 参数则会允许手动调整更多选项，在本教程中是必须的。

.. code-block:: bash

   $ gpg --full-gen-key --expert

基于安全考虑，主密钥它仅用于签发子密钥，但不用于加密和签名。主密钥的强度要足够高，但考虑到目前计算机的算力与成本，即便在量子计算机面前，密钥长度较大的RSA密钥依然是足够安全的。因此，这里选择用 RSA 算法签发 4096 位的主密钥。

.. code-block:: bash

   gpg (GnuPG) 2.2.4; Copyright (C) 2017 Free Software Foundation, Inc.
   This is free software: you are free to change and redistribute it.
   There is NO WARRANTY, to the extent permitted by law.

   Please select what kind of key you want:
      (1) RSA and RSA (default)
      (2) DSA and Elgamal
      (3) DSA (sign only)
      (4) RSA (sign only)
      (7) DSA (set your own capabilities)
      (8) RSA (set your own capabilities)
      (9) ECC and ECC
     (10) ECC (sign only)
     (11) ECC (set your own capabilities)
     (13) Existing key
   Your selection? 8

分别取消主密钥的“加密（Encrypt）”与“签名（Sign）”功能，只留下“认证（Certify）”功能，然后选择“完成（Finished）”。

.. code-block:: bash

   Possible actions for a RSA key: Sign Certify Encrypt Authenticate
   Current allowed actions: Sign Certify Encrypt

      (S) Toggle the sign capability
      (E) Toggle the encrypt capability
      (A) Toggle the authenticate capability
      (Q) Finished

   Your selection? s

   Possible actions for a RSA key: Sign Certify Encrypt Authenticate
   Current allowed actions: Certify Encrypt

      (S) Toggle the sign capability
      (E) Toggle the encrypt capability
      (A) Toggle the authenticate capability
      (Q) Finished

   Your selection? e

   Possible actions for a RSA key: Sign Certify Encrypt Authenticate
   Current allowed actions: Certify

      (S) Toggle the sign capability
      (E) Toggle the encrypt capability
      (A) Toggle the authenticate capability
      (Q) Finished

   Your selection? q

设置 RSA 主密钥长度为 4096。

.. code-block:: bash

   RSA keys may be between 1024 and 4096 bits long.
   What keysize do you want? (3072) 4096
   Requested keysize is 4096 bits

设置主密钥的过期时间，可以设置为永不过期。

.. code-block:: bash

   Please specify how long the key should be valid.
            0 = key does not expire
         <n>  = key expires in n days
         <n>w = key expires in n weeks
         <n>m = key expires in n months
         <n>y = key expires in n years
   Key is valid for? (0)
   Key does not expire at all

根据提示输入主密钥的标识信息。

.. code-block:: bash

   Is this correct? (y/N) y

   GnuPG needs to construct a user ID to identify your key.

   Real name: marisa
   Email address: marisa@jinkan.org
   Comment: Kirisame Marisa
   You selected this USER-ID:
       "marisa (Kirisame Marisa) <marisa@jinkan.org>"

   Change (N)ame, (C)omment, (E)mail or (O)kay/(Q)uit? o

接下来会提示你输入用于保护主密钥的密码。

.. code-block:: bash

   ┌─────────────────────────────────────────────────────┐
   │ Please enter the passphrase to                      │
   │ protect your newkey                                 │
   │                                                     │
   │ Passphrase:_______________________________________  │
   │                                                     │
   │      <OK>                             <Cancel>      │
   └─────────────────────────────────────────────────────┘

设置好密码后，GnuPG 会收集系统中的熵生成随机数据以生成RSA算法所需的素数。如果 CPU 实现了硬件随机数生成器，这个过程会很快完成，否则会需要一些时间。敲击键盘、移动鼠标、读写磁盘都可以产生熵，加速这个过程。

如果是在虚拟机中运行 GnuPG，则会因为 Hypervisor 屏蔽了 CPU 的硬件随机数生成器而变慢。

.. code-block:: bash

   We need to generate a lot of random bytes. It is a good idea to perform
   some other action (type on the keyboard, move the mouse, utilize the
   disks) during the prime generation; this gives the random number
   generator a better chance to gain enough entropy.
   gpg: key E6ED69D1C9149F9B marked as ultimately trusted
   gpg: revocation certificate stored as '/home/yinian/.gnupg/openpgp-revocs.d/7046C3E8C8DD73F814FDE289E6ED69D1C9149F9B.rev'
   public and secret key created and signed.

   pub   rsa4096 2020-04-29 [C]
         7046C3E8C8DD73F814FDE289E6ED69D1C9149F9B
   uid                      marisa (Kirisame Marisa) <marisa@jinkan.org>

至此，就成功生成了一个主密钥。运行\ ``gpg -k``\ 命令列出所有公钥，即可看到刚刚生成的主密钥。

.. code-block:: bash

   $ gpg -k
   /home/yinian/.gnupg/pubring.kbx
   -------------------------------
   pub   rsa4096 2020-04-29 [C]
         7046C3E8C8DD73F814FDE289E6ED69D1C9149F9B
   uid           [ultimate] marisa (Kirisame Marisa) <marisa@jinkan.org>

第二步：添加子密钥
------------------

我们已经生成了长度 4096 位的 RSA 主密钥，只启用了“认证（Certify）”功能，在这一步将会用它来签发子密钥。我们将为“加密（Encrypt）”、“签名（Signing）”、“身份验证（Authentication）”功能分别生成独立的子密钥。

我们用\ ``--edit-key``\ 编辑已经生成好的主密钥，进入\ ``gpg``\ 提示符模式，这一步同样需要\ ``--expert``\ 参数来调整更多选项。

.. code-block:: bash

   gpg (GnuPG) 2.2.4; Copyright (C) 2017 Free Software Foundation, Inc.
   This is free software: you are free to change and redistribute it.
   There is NO WARRANTY, to the extent permitted by law.

   Secret key is available.

   sec  rsa4096/E6ED69D1C9149F9B
        created: 2020-04-29  expires: never       usage: C
        trust: ultimate      validity: ultimate
   [ultimate] (1). marisa (Kirisame Marisa) <marisa@jinkan.org>

   gpg>

下面开始添加第一个子密钥，键入\ ``addkey``\ 命令后会提示选择密钥算法。因为子密钥将用于文件、邮件的加密解密以及 SSH 身份验证等操作，为了兼顾运算速度与安全性，为子密钥选择椭圆曲线算法。第一个子密钥用于签名。

.. code-block:: bash

   Please select what kind of key you want:
      (3) DSA (sign only)
      (4) RSA (sign only)
      (5) Elgamal (encrypt only)
      (6) RSA (encrypt only)
      (7) DSA (set your own capabilities)
      (8) RSA (set your own capabilities)
     (10) ECC (sign only)
     (11) ECC (set your own capabilities)
     (12) ECC (encrypt only)
     (13) Existing key
   Your selection? 10

之后会提示选择用于签发密钥的椭圆曲线。其中美国国家标准与技术研究院（NIST）系列椭圆曲线、Brainpool 系列椭圆曲线、secp256k1 都存在不同的安全风险，不予考虑。尤其是 NIST 与 NSA 说不清道不明的关系，可能是故意留下的弱化实现。

25519 椭圆曲线是最快的椭圆曲线之一，而且没有专利壁垒，是公有领域的产品，在 2013 年NSA的 Dual_EC_DRBG 后门爆出之后备受关注。目前，25519 曲线作为 P-256 的成功后继替代，在众多应用中广泛使用，支持良好。

本教程中的子密钥都选择了“Curve 25519”。

.. code-block:: bash

   Please select which elliptic curve you want:
      (1) Curve 25519
      (3) NIST P-256
      (4) NIST P-384
      (5) NIST P-521
      (6) Brainpool P-256
      (7) Brainpool P-384
      (8) Brainpool P-512
      (9) secp256k1
   Your selection? 1

同样也要为子密钥设置过期时间，这里设置为 3 年。

.. code-block:: bash

   Please specify how long the key should be valid.
            0 = key does not expire
         <n>  = key expires in n days
         <n>w = key expires in n weeks
         <n>m = key expires in n months
         <n>y = key expires in n years
   Key is valid for? (0) 3y
   Key expires at Sat 29 Apr 2023 10:10:03 PM CST
   Is this correct? (y/N) y

在最终确认并输入主密钥密码后，又迎来了随机素数生成环节。随后，在结果中可以看到新生成的子密钥。

.. code-block:: bash

   Really create? (y/N) y
   We need to generate a lot of random bytes. It is a good idea to perform
   some other action (type on the keyboard, move the mouse, utilize the
   disks) during the prime generation; this gives the random number
   generator a better chance to gain enough entropy.

   sec  rsa4096/E6ED69D1C9149F9B
        created: 2020-04-29  expires: never       usage: C
        trust: ultimate      validity: ultimate
   ssb  ed25519/0603637C77817467
        created: 2020-04-29  expires: 2023-04-29  usage: S
   [ultimate] (1). marisa (Kirisame Marisa) <marisa@jinkan.org>

同理，继续生成“加密（Encrypt）”的独立子密钥。

.. code-block:: bash

   gpg> addkey
   Please select what kind of key you want:
      (3) DSA (sign only)
      (4) RSA (sign only)
      (5) Elgamal (encrypt only)
      (6) RSA (encrypt only)
      (7) DSA (set your own capabilities)
      (8) RSA (set your own capabilities)
     (10) ECC (sign only)
     (11) ECC (set your own capabilities)
     (12) ECC (encrypt only)
     (13) Existing key
   Your selection? 12
   （以下省略）

生成用于“身份验证（Authentication）”的独立子密钥。

.. code-block:: bash

   gpg> addkey
   Please select what kind of key you want:
      (3) DSA (sign only)
      (4) RSA (sign only)
      (5) Elgamal (encrypt only)
      (6) RSA (encrypt only)
      (7) DSA (set your own capabilities)
      (8) RSA (set your own capabilities)
     (10) ECC (sign only)
     (11) ECC (set your own capabilities)
     (12) ECC (encrypt only)
     (13) Existing key
   Your selection? 11

   Possible actions for a ECDSA/EdDSA key: Sign Authenticate
   Current allowed actions: Sign

      (S) Toggle the sign capability
      (A) Toggle the authenticate capability
      (Q) Finished

   Your selection? s

   Possible actions for a ECDSA/EdDSA key: Sign Authenticate
   Current allowed actions:

      (S) Toggle the sign capability
      (A) Toggle the authenticate capability
      (Q) Finished

   Your selection? a

   Possible actions for a ECDSA/EdDSA key: Sign Authenticate
   Current allowed actions: Authenticate

      (S) Toggle the sign capability
      (A) Toggle the authenticate capability
      (Q) Finished

   Your selection? q
   （以下省略）

最后一个子密钥生成结束后，就会得到如下结果。键入\ ``quit``\ 推出\ ``gpg``\ 提示符模式，并保存子密钥生成的结果。

.. code-block:: bash

   sec  rsa4096/E6ED69D1C9149F9B
        created: 2020-04-29  expires: never       usage: C
        trust: ultimate      validity: ultimate
   ssb  ed25519/0603637C77817467
        created: 2020-04-29  expires: 2023-04-29  usage: S
   ssb  cv25519/92DB4B74B547C0C4
        created: 2020-04-29  expires: 2023-04-29  usage: E
   ssb  ed25519/3D8F29BC6F58D6B8
        created: 2020-04-29  expires: 2023-04-29  usage: A
   [ultimate] (1). marisa (Kirisame Marisa) <marisa@jinkan.org>

   gpg> quit
   Save changes? (y/N) y

第三步：备份、发布与吊销
------------------------

主密钥可以签发具有实际功能的子密钥，如果主密钥失窃，攻击者则可以利用主密钥肆意签发子密钥，破译你的加密文件或通信内容，伪造你的身份信息，因此要妥善主密钥的私钥。

备份
~~~~

因为笔者家境贫寒，难以负担得起智能卡（比如 YubiKey）的费用，只能演示一种古老而朴素的备份方法：把主密钥私钥导出成文件，保存到单独的U盘中。

执行下面的命令，首先备份所有密钥的私钥，放置到一个妥善的地方。其中\ ``-a``\ 参数是\ ``--armor``\ 参数的简写形式，这个参数让\ ``gpg``\ 把输出内容编码成ASCII。

.. code-block:: bash

   $ gpg -a --export-secret-key marisa@jinkan.org > secret_key

再单独导出子密钥的私钥。

.. code-block:: bash

   $ gpg -a --export-secret-subkeys marisa@jinkan.org > secret_subkeys

考虑到在未来，因为私钥泄露或其他原因想要吊销主密钥，就需要用到吊销证书。我们先导出主密钥的吊销证书。

.. code-block:: bash

   $ gpg -a --gen-revoke marisa@jinkan.org > revocation_cert

   sec  rsa4096/E6ED69D1C9149F9B 2020-04-29 marisa (Kirisame Marisa) <marisa@jinkan.org>

   Create a revocation certificate for this key? (y/N) y
   Please select the reason for the revocation:
     0 = No reason specified
     1 = Key has been compromised
     2 = Key is superseded
     3 = Key is no longer used
     Q = Cancel
   (Probably you want to select 1 here)
   Your decision? 1
   Enter an optional description; end it with an empty line:
   >
   Reason for revocation: Key has been compromised
   (No description given)
   Is this okay? (y/N) y
   Revocation certificate created.

   Please move it to a medium which you can hide away; if Mallory gets
   access to this certificate he can use it to make your key unusable.
   It is smart to print this certificate and store it away, just in case
   your media become unreadable.  But have some caution:  The print system of
   your machine might store the data and make it available to others!

然后删除主密钥和所有子密钥的私钥。

.. code-block:: bash

   $ gpg --delete-secret-keys marisa@jinkan.org
   gpg (GnuPG) 2.2.4; Copyright (C) 2017 Free Software Foundation, Inc.
   This is free software: you are free to change and redistribute it.
   There is NO WARRANTY, to the extent permitted by law.

   sec  rsa4096/E6ED69D1C9149F9B 2020-04-29 marisa (Kirisame Marisa) <marisa@jinkan.org>

   Delete this key from the keyring? (y/N) y
   This is a secret key! - really delete? (y/N) y

用\ ``-K``\ 参数列出私钥，没有返回结果，则删除成功。

.. code-block:: bash

   $ gpg -K
   $

然后导入刚刚导出的所有子密钥的私钥。

.. code-block:: bash

   $ gpg --import secret_subkeys
   gpg: key E6ED69D1C9149F9B: "marisa (Kirisame Marisa) <marisa@jinkan.org>" not changed
   gpg: To migrate 'secring.gpg', with each smartcard, run: gpg --card-status
   gpg: key E6ED69D1C9149F9B: secret key imported
   gpg: Total number processed: 1
   gpg:              unchanged: 1
   gpg:       secret keys read: 1
   gpg:   secret keys imported: 1

再次用\ ``-K``\ 参数列出私钥，可以看到主密钥私钥一行\ ``sec``\ 后有了一个\ ``#``\ 字符，这说明缺失主密钥的私钥，也即成功离线备份了主密钥的私钥。

发布
----

我们需要导出公钥发送给他人或直接发布到公钥服务器上，才能让你的密钥有实际用途。若是发布后出现了安全问题，则需要使用吊销证书吊销密钥。

可以把公钥发布成文本。

.. code-block:: bash

   $ gpg -a --export marisa@jinkan.org > public.gpg

也可以发布到密钥服务器上。

.. code-block:: bash

   $ gpg --send-keys marisa@jinkan.org --keyserver hkps://hkps.pool.sks-keyservers.net

吊销
----

如果还能找到“妥善保管”的吊销证书，则可以吊销密钥。

.. code-block:: bash

   $ gpg --import revocation_cert
   gpg: key E6ED69D1C9149F9B: "marisa (Kirisame Marisa) <marisa@jinkan.org>" revocation certificate imported
   gpg: Total number processed: 1
   gpg:    new key revocations: 1
   gpg: marginals needed: 3  completes needed: 1  trust model: pgp
   gpg: depth: 0  valid:   1  signed:   0  trust: 0-, 0q, 0n, 0m, 0f, 1u

无论是用\ ``-k``\ 还是\ ``-K``\ 参数，都可以看到密钥已被吊销。

.. code-block:: bash

   $ gpg -K
   /home/yinian/.gnupg/pubring.kbx
   -------------------------------
   sec   rsa4096 2020-04-29 [C] [revoked: 2020-04-30]
         7046C3E8C8DD73F814FDE289E6ED69D1C9149F9B
   uid           [ revoked] marisa (Kirisame Marisa) <marisa@jinkan.org>

如果之前已经发布到密钥服务器上，还需要用\ ``--send-keys``\ 参数重新发布吊销信息。

.. code-block:: bash

   $ gpg --send-keys marisa@jinkan.org --keyserver hkps://hkps.pool.sks-keyservers.net

在等待一段时间后，整个密钥服务器网络将都会显示正确的吊销状态。

结语
====

本文只是简单的 GnuPG 操作流程介绍，给出了一种较为安全的密钥管理方法，关于 GnuPG 的详细介绍敬请期待 NT 老师的系列讲解。

另外，运行如下命令即可获取我的 GnuPG 公钥。

.. code-block:: bash

   gpg --recv-keys 2FD95EA61B41F507
