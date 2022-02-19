SRCDS 安装笔记
##############
:date: 2013-02-15 23:26
:author: yinian
:category: Uncategoried
:tags: Games, SRCDS, Steam
:slug: srcds-installation
:status: published

准备工作
--------

（参考 ` <http://forums.srcds.com/showthread.php?tid=736&pid=3508#pid3508>`__\ ` <http://forums.srcds.com/showthread.php?tid=736&pid=3508#pid3508>`__\ http://forums.srcds.com/showthread.php?tid=736&pid=3508#pid3508\ ）

安装 uncompress 或：

.. code:: shell

   $ ln -s /usr/bin/gunzip /usr/bin/uncompress

使 uncompress 命令可用。

安装
----

HLDS 更新工具
~~~~~~~~~~~~~

在合适的位置下载 HLDSUpdatetool：

.. code:: shell

   $ mkdir srcds
   $ cd srcds
   $ wget http://www.steampowered.com/download/hldsupdatetool.bin
   $ chmod +x hldsupdatetool.bin
   $ ./hldsupdatetool.bin
   $ ./steam

此时 srcds 目录下会有 test1.so、test2.so 和 test3.so 几个文件。

下载游戏
~~~~~~~~

此命令会从 Steam 服务器上下载游戏和服务器版本文件。

.. code:: shell

   $ ./steam -command update -game "" -dir . -username  -password 

game 参数后的游戏名称见 Dedicated Server Name Enumeration 的 update 列。

防火墙
~~~~~~

（参考 ` <http://www.freenerd.net/index.php?title=IPTABLES_for_SRCDS>`__\ http://www.freenerd.net/index.php?title=IPTABLES_for_SRCDS\ ）

根据 Steam 使用的端口范围：

| Steam Main - UDP 27000 - 27015
| Steam Main - TCP 27020 - 27039
| Steam CyberCafe - TCP 27040 - 27041
| Steam Friends - UDP 1200
| Steam Dedicated Server - UDP 27015 - 27050
| Steam HLTV - UDP 27020
| Rcon - TCP - 与你 SRCDS 游戏服务器使用的相同
| 设置 iptables 规则：

::

   -A INPUT -m udp -p udp --dport 27000:27020 -j ACCEPT
   -A INPUT -m udp -p udp --dport 1200 -j ACCEPT
   -A INPUT -m tcp -p tcp --dport 27000:27050 -j ACCEPT
   -A INPUT -m udp -p udp --dport 27000:27050 -j ACCEPT

启动
----

以 Counter-Striker:Source 为例：

.. code:: shell

   $ cd css
   $ ./srcds_run -console -game cstrike +map de_dust -maxplayers 16 -autoupdate

game 参数后的游戏名称见 Dedicated Server Name Enumeration 的 launch 列。
