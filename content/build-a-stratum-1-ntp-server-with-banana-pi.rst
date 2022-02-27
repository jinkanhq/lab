用 Banana Pi 实现一台 Stratum 1 的 NTP 服务器
#############################################
:date: 2020-09-21 21:57
:author: yinian
:category: Uncategoried
:tags: ARM, Armbian, Banana Pi, GPS, NTP, PPS
:slug: build-a-stratum-1-ntp-server-with-banana-pi
:status: published
:feature: /images/2020/pexels-skitterphoto-9352.jpg
:abstract: 由于笔者家境贫寒，翻箱倒柜只能找出一台闲置多年积了厚厚一层灰的香蕉派（Banana Pi BPI-M1），并不能适配树莓派的教程，也就有了这篇笔记。

1 前言
======

笔者在某个不可多说的离线环境下屡屡遭受系统时钟不准确带来的诡异问题，经与多方交涉未果，便决定自己动手，利用卫星授时的方式自建一台低成本的Stratum-1 NTP服务器，为离线环境提供准确可靠的授时服务。网上已经有很多用树莓派（Raspberry Pi）制作NTP服务器的教程，但由于笔者家境贫寒，翻箱倒柜只能找出一台闲置多年积了厚厚一层灰的香蕉派（Banana Pi BPI-M1），并不能适配树莓派的教程，也就有了这篇笔记。

1.1 香蕉派
----------

香蕉派（Banana Pi）是深圳市源创通信技术有限公司的低成本、卡片大小的单板计算机（SBC，Single Board Computer）系列产品，与树莓派很是相似。笔者的Banana Pi BPI-M1是该系列最早的型号，它配备有一颗全志A20双核Cortex-A7 CPU和1 GB DDR 3内存，提供了千兆网口和SATA接口，无论是性能还是接口都超越了同时期的树莓派。

1.2 卫星导航接收机
------------------

在万能的淘宝上搜索GPS/北斗模块等字样，能找到许多价格便宜的成品模块，其中USB接口的模块价格较高，而且会受到USB接口本身的限制，授时抖动（Jitter）较高，不予考虑。本文选取了带有6PIN接口的模块，分别把供电、U-ART和PPS针脚连接到香蕉派的GPIO接口。

.. image:: /images/2020/taobao-search.jpg

笔者为了偷懒，省去布置室外天线的麻烦，选择了一体陶瓷天线的版本。

1.3 PPS
-------

秒脉冲（PPS/1PPS，Pulse Per Second）一般是由卫星导航接收机或原子钟按秒发出的、宽度小于1秒、有着急升或突降边沿的脉冲信号，通常用于精确计时和测量时间。PPS信号能精确地（亚毫秒级）指示每一秒的开始时间，但不能指示对应现实时间的哪一秒，因此只能作为辅助信号，与卫星导航信息组合使用，提供低延迟、低抖动的授时服务。

1.4 Stratum
-----------

`Stratum <https://docs.ntpsec.org/latest/ntpspeak.html#stratum>`_\ 是NTP中表示时间服务器层级的术语。基准时钟（\ `refclock <https://docs.ntpsec.org/latest/ntpspeak.html#refclock>`_\ ，Reference Clock）是Stratum 0；直接连接到基准时钟的服务器是Stratum 1；连接到Stratum N服务器的客户端是Stratum N+1。N的数值越大，距离基准时钟越远，也就越不精准。N的最大值是16，表示该设备未同步且不可达。大多数公共时间服务器是Stratum 1或Stratum 2。

2 系统安装
==========

Armbian是一个面向单板计算机的轻量级Linux发行版，有基于Ubuntu和基于Debian的两种版本。本文选用了基于 Ubuntu Focal 20.04 LTS 的 Armbian 作为香蕉派运行的操作系统，下载地址如下。

-  官方地址：\ https://redirect.armbian.com/bananapi/Focal_current
-  清华镜像：\ https://mirrors.tuna.tsinghua.edu.cn/armbian-releases/bananapi/archive/Armbian_20.08.1_Bananapi_focal_current_5.8.5.img.xz

2.1 写入镜像
------------

镜像下载完成后用 ``gpg`` 校验镜像是否完整且可靠。签名文件下载地址如下。

-  官方地址：\ https://redirect.armbian.com/bananapi/Focal_current.asc
-  清华镜像：\ https://mirrors.tuna.tsinghua.edu.cn/armbian-releases/bananapi/archive/Armbian_20.08.1_Bananapi_bionic_current_5.8.5.img.xz.asc

.. code-block:: bash

   $ gpg --keyserver ha.pool.sks-keyservers.net --recv-key DF00FAF1C577104B50BF1D0093D6889F9F0E78D5
   $ gpg --verify Armbian_20.08.1_Bananapi_bionic_current_5.8.5.img.xz.asc

若输出如下提示，则镜像内容无误，可以进行下一步。

.. code-block:: bash

   gpg: assuming signed data in 'Armbian_20.08.1_Bananapi_focal_current_5.8.5.img.xz'
   gpg: Signature made Wed Sep  2 22:58:09 2020 CST
   gpg:                using RSA key DF00FAF1C577104B50BF1D0093D6889F9F0E78D5
   gpg: Good signature from "Igor Pecovnik <igor@armbian.com>" [unknown]
   gpg:                 aka "Igor Pecovnik (Ljubljana, Slovenia) <igor.pecovnik@gmail.com>" [unknown]

在 Windows 下可以用 `Win32DiskImager <https://sourceforge.net/projects/win32diskimager/>`__ 之类的工具把 img 格式的镜像写入到 SD 卡；在 Linux 下则可以直接使用 ``dd`` 命令。人间实验室友情提醒您，安全千万条，手贱第一条。\ **注意确保选择正确的盘符或设备，写入镜像的设备会丢失包括分区表在内的所有数据。**

写入完成之后即可在香蕉派上从 SD 启动 Armbian，默认的用户名是 ``root``\ ，密码是 ``1234`` 。成功登入后可以见到如下提示。

|image1|

.. class:: center

Welcome to Ubuntu 20.04 with Linux 5.8.5

2.2 软件源
----------

为了避免在多说无益的国际出口上浪费时间，需要替换软件源地址，以清华镜像为例。

.. code-block:: bash

   $ sudo sed -i "s/ports.ubuntu.com/mirrors.tuna.tsinghua.edu.cn\/ubuntu-ports/g" /etc/apt/sources.list
   $ sudo sed -i "s/apt.armbian.com/mirrors.tuna.tsinghua.edu.cn\/armbian/g" /etc/apt/sources.list.d/armbian.list

获取更新信息并更新 Armbian 到最新版本。

.. code-block:: bash

   $ sudo apt update && apt upgrade

3 卫星授时
==========

在先决基础环境配置完毕后，下面就可以组装 NTP 服务器的部件了。

3.1 连接
========

根据全志 A20 说明书及香蕉派的针脚定义，笔者按照下表把卫星导航接收机连接到香蕉派 GPIO 接口。

================== ========== ============== ===========
卫星导航接收机针脚 香蕉派针脚 香蕉派针脚定义 A20针脚定义
================== ========== ============== ===========
V                  CON3-P02   VCC-5V         
R                  CON3-P08   UART3-TX       PH0
T                  CON3-P10   UART3-RX       PH1
G                  CON3-P06   GND            
P                  CON3-P12   IO-1           PH2
================== ========== ============== ===========

``V:VCC`` 为 5V 供电接口；\ ``G:GND`` 为接地；\ ``R:UART3-TX`` 与 ``T:UART3-RX`` 为一组通用通用异步收发传输器（UART，Universal Asynchronous Receiver/Transmitter），连接到全志 A20 上序号为 3 的 UART 控制器，在 Armbian 中体现为一个 ``/dev/ttyS#`` 串口设备；\ ``P:IO-1`` 是秒脉冲（PPS，Pulse Per Second）信号，在 Armbian 中体现为一个 ``/dev/pps#`` 设备。

3.2 驱动
========

要在 Armbian 中使用上述的 ``/dev/ttyS#`` 和 ``/dev/pps#`` 设备，仅仅是接好线是不够的，还要按照具体接口使用情况配置上述设备的驱动。

Armbian 采用 U-Boot 作为引导加载程序（Boot Loader），并为全志 A20 预定义了丰富的设备树覆盖（Device Tree Overlay）。这里只需要按照 `Armbian 文档 <https://docs.armbian.com/User-Guide_Allwinner_overlays/>`__\ 修改 ``/boot/armbianEnv.txt`` 文件，重启后即可按照其中的配置加载驱动，而不用费力修改驱动源码中的预定义针脚，省去了自行编译驱动的琐碎步骤。

Armbian 支持的所有全志 A20 设备树覆盖见 https://github.com/armbian/sunxi-DT-overlays/blob/master/sun7i-a20/README.sun7i-a20-overlays\ 。本文仅涉及其中的两项设备驱动：\ ``uart3`` 和 ``pps-gpio``\ 。

修改 ``/boot/armbianEnv.txt`` 文件，添加如下内容。

.. code-block:: ini

   overlay_prefix=sun7i-a20
   overlays=uart3 pps-gpio
   param_uart3_pins=b
   param_pps_pin=PH2

其中 ``param_uart3_pins`` 设置为 ``b`` 时，则指定 UART3 的 TX、RX 针脚分别为 PH0、PH1。

这样，驱动的配置就与实际针脚连接情况一致了，接下来测试设备是否运行正常。首先是 UART3 设备，可以用 ``dmesg | grep ttyS`` 找到实际设备名并尝试访问。如果卫星导航接收机工作正常，并能与香蕉派正常通信，以 ``/dev/ttyS1`` 为例，输出类似如下的 NMEA 语句。

.. code-block:: bash

   $ cat /dev/ttyS1
   $BDGSV,4,4,06,42,,,24,0*71
   $GNRMC,055355.000,V,,,,,,,210920,,,N,V*22
   $GNZDA,055355.000,21,09,2020,00,00*41
   $GPTXT,01,01,01,ANTENNA OPEN*25

同样，用 ``dmesg | grep pps`` 找出 PPS 的实际设备名，安装 PPS 工具集 ``pps-tools``\ ，用 ``ppstest`` 命令来测试 PPS 设备，以 ``/dev/pps0`` 为例，会输出类似如下的内容。

.. code-block:: bash

   $ sudo apt install pps-tools
   $ sudo ppstest /dev/ppsx
   trying PPS source "/dev/pps0"
   found PPS source "/dev/pps0"
   ok, found 1 source(s), now start fetching data...
   source 0 - assert 1600694355.999955687 sequence: 42 - clear  0.000000000, sequence: 0
   source 0 - assert 1600694356.999955419 sequence: 43 - clear  0.000000000, sequence: 0
   source 0 - assert 1600694357.999955141 sequence: 44 - clear  0.000000000, sequence: 0

如果卫星导航接收机没能获取定位信息（信号不佳或正在启动），那么不会输出 PPS 型号，则会报错。

.. code-block:: bash

   trying PPS source "/dev/pps0"
   found PPS source "/dev/pps0"
   ok, found 1 source(s), now start fetching data...
   time_pps_fetch() error -1 (Connection timed out)
   time_pps_fetch() error -1 (Connection timed out)
   time_pps_fetch() error -1 (Connection timed out)

3.3 NTP
=======

首先安装 NTP 服务器。

.. code-block:: bash

   $ sudo apt install ntp

修改 NTP 配置文件，在末尾添加如下内容。

.. code-block:: bash

   # Generic NMEA GPS Receiver
   server 127.127.20.x mode 16 minpoll 4 maxpoll 4 prefer
   fudge 127.127.20.x refid GPS
   # PPS GPIO
   server 127.127.22.x minpoll 4 maxpoll 4 true
   fudge 127.127.22.x refid PPS

其中 GPS 部分的 ``127.127.20.x`` 为 NTP 中 NMEA 驱动的服务器地址，最后一位的 ``x`` 要替换成 GPS 设备 ``/dev/gpsx`` 的序号。但实际上卫星导航接收机的设备是 ``/dev/ttyS1`` ，这里做一个软连接以供 NTP 使用。

.. code-block:: bash

   $ sudo ln -s /dev/ttyS1 /dev/gps1

此时地址应为 ``127.127.20.1`` 。

``mode`` 的取值含义见下表。

== == =========================
位 值 定义
== == =========================
0  1  处理 NMEA 语句 RMC
1  2  处理 NMEA 语句 GGA
2  4  处理 NMEA 语句 GLL
3  8  处理 NMEA 语句 ZDA 和 ZDG
4  16 波特率 9600
5  24 波特率 19200
6  32 波特率 38400
== == =========================

``mode`` 的 0~3 位取 0 时处理所有 NMEA 语句，是默认配置。4~6 位取 0 时波特率为 4800，是默认配置。此处 ``mode 16`` 即是处理所有 NMEA 语句，波特率为 9600，匹配卫星导航接收机的参数。

虽然 NTP 中的通用 GPS NMEA 驱动名为 ``GPS``\ ，但实际上它能\ `解析所有符合 NMEA 标准的语句 <https://github.com/ntp-project/ntp/blob/9c75327c3796ff59ac648478cd4da8b205bceb77/ntpd/refclock_nmea.c#L849>`__\ ，而不是只能支持美国的 GPS。

其中 PPS 部分 ``127.127.22.x`` 为 NTP 中 PPS 驱动的服务器地址，与 NMEA 驱动一样，最后一位的 ``x`` 要替换成 PPS 设备 ``/dev/ppsx`` 的序号。

之后重启 NTP 服务，用 ``ntpq`` 命令检查 GPS 和 PPS 授时状态。

.. code-block:: bash

   $ sudo systemctl restart ntp
   $ ntpq -p
       remote           refid       st t when poll reach   delay   offset  jitter
   ==============================================================================
   *GPS_NMEA(1)     .GPS.            0 l    3   16  377    0.000    0.334   1.082
   oPPS(0)          .PPS.            0 l    6   16  377    0.000   -0.267   0.191

让 NTP 保持运行一段时间，收集足够的样本，可以看出 PPS 的抖动（Jitter）只有亚毫秒级。如果不是有严苛要求的特殊场景，这个结果已经足够好了。

.. |image1| image:: /images/2020/mariya-e1600866909605.jpg
