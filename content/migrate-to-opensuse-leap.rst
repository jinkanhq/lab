迁移到 openSUSE Leap
####################
:date: 2021-06-29 21:06
:author: yinian
:category: Uncategoried
:tags: firewalld, kvm, libvirt, linux, openSUSE
:slug: migrate-to-opensuse-leap
:status: published
:feature: /images/2021/opensuse-cover.jpg
:abstract: 在 NT 坚持不懈地营业推销下，笔者终于鼓起勇气把搬砖机系统换成了 openSUSE Leap，投入 KDE 的怀抱

1. 前言
===========

笔者不可多说的离线环境中有一台心爱的民族品牌搬砖机，可怜的 Intel 核显只有陈年 2K 屏与之为伴。这时的 Ubuntu 与 GNOME 就成为了双倍的\ [STRIKEOUT:喜悦]\ 摧残，尤其是分数倍缩放的掉帧、画面撕裂，让每一次窗口切换、调整大小都成了立体主义的现场表演。在 NT 坚持不懈地营业推销下，笔者终于鼓起勇气把搬砖机系统换成了 openSUSE Leap，投入 KDE 的怀抱。

2. openSUSE 近况
===================

openSUSE 在国内的人气远没有 Ubuntu 和 CentOS 高，其中有一些历史原因，背后的商业版本 SUSE 几易东家，让 openSUSE 错过了许多发展机会。直到 2015 年的秋天，openSUSE 发布了全新的发型版 Leap ，版本号大跨进至 42.1（上一个版本是 13.2），这个 42 就是《银河系漫游指南》系列科幻小说中提到的“生命、万物与一切”问题的终极答案，这个版本对于 openSUSE 的意义可见一斑。

Leap 的地位差不多对等于 RedHat 系的社区版本 CentOS，一经问世就强调与企业版的 SLES 的血缘关系，它的基础包全部来源于 SLES，而应用程序和桌面环境则来源于另一套 openSUSE 发行版——风滚草（Tumbleweed，TW）。预计今年 7 月发布的 Leap 15.3 中，Leap 与 SLES 的差距将继续缩小，二者\ `共用相同的源码和二进制包 <https://www.suse.com/c/closing-the-leap-gap-src/>`__\ 。

Tumbleweed（风滚草）比 Leap 稍微年长一些，是在 2014 年 11 月与openSUSE 的 Factory 代码库合并，成为单独的发行版，滚动更新至今。与偏向稳健的 Leap 不同，Tumbleweed 更适合喜欢紧跟前沿的 openSUSE 老手和软件开发人员。

因为 Tumbleweed 中内核版本更新非常频繁，如果你不熟悉内核模块的编译安装方法，并且使用了需要第三方驱动（比如显卡）的硬件，请不要使用它！

因为笔者的搬砖环境是离线的，也只能屈服于 Leap 的安逸了。

3. Zypper
============

openSUSE 与 RedHat 系一样，使用 RPM 包，但不用\ ``yum``\ ，而且互不通用。openSUSE 中的包管理工具有 3 种。

#. 命令行的\ ``zypper``
#. 图形界面的 YaST
#. 底层的\ ``rpm``\ 命令

其中 Zypper 和 YaST 都是包管理引擎 `libzypp <https://doc.opensuse.org/projects/libzypp/HEAD/>`__ 的具体实现。

在国内网络环境使用，要改成国内的软件源镜像，首先禁用当前所有仓库。

.. code-block:: bash

   sudo zypper mr -da

然后添加国内软件源镜像，以腾讯云为例。

.. code-block:: bash

   sudo zypper ar -fcg https://mirrors.cloud.tencent.com//opensuse/distribution/leap/\$releasever/repo/oss/ tuna-oss
   sudo zypper ar -fcg https://mirrors.cloud.tencent.com//opensuse/distribution/leap/\$releasever/repo/non-oss/ tuna-non-oss
   sudo zypper ar -fcg https://mirrors.cloud.tencent.com//opensuse/update/leap/\$releasever/oss/ tuna-update-oss
   sudo zypper ar -fcg https://mirrors.cloud.tencent.com//opensuse/update/leap/\$releasever/non-oss/ tuna-update-non-oss

参数\ ``-fcg``\ 中的\ ``f``\ 和\ ``g``\ 分别启用了仓库的刷新（Refresh）、GPG 校验（GPG Check）功能。

``zypper``\ 的常见用法见下。

.. code-block:: bash

   zypper ref # 刷新仓库
   zypper patch # 安装所有可用补丁
   zypper up # 更新所有已安装的包
   zypper in docker-compose # 安装 Docker Compose
   zypper in -t pattern devel_basis # 安装 Base Development 模式
   zypper rm docker-compose # 卸载 Docker Compose
   zypper search pinyin # 搜索与 pinyin 有关的包

5. KVM
============

.. code-block:: bash

   $ qemu-system-x86_64 --version
   QEMU emulator version 5.2.0 (SUSE Linux Enterprise 15)
   Copyright (c) 2003-2020 Fabrice Bellard and the QEMU Project developers

openSUSE 自带的 qemu 版本足够新（默认启用\ ``pc-q35-5.2``\ ），但默认配置下的 Windows 10 虚拟机 CPU 占用率明显过高。这里根据 KVM 开发者 Vitaly Kuznetsov 的\ `说明 <https://bugzilla.redhat.com/show_bug.cgi?id=1738244#c6>`__\ ，手动添加一些配置，即可明显降低 CPU 占用到合理值。

在\ ``<hyper-v>``\ 段加入如下内容。

.. code-block:: xml

   <relaxed state='on'/>
   <vapic state='on'/>
   <spinlocks state='on' retries='8191'/>
   <vpindex state='on'/>
   <synic state='on'/>
   <stimer state='on'/>

在\ ``<clock>``\ 段中加入如下内容。

.. code-block:: xml

   <clock offset='localtime'>
       <timer name='rtc' tickpolicy='catchup'/>
       <timer name='pit' tickpolicy='delay'/>
       <timer name='hpet' present='no'/>
       <timer name='hypervclock' present='yes'/>
   </clock>

6. 网络
===================

笔者在用 CentOS / Ubuntu 时就有领略到 NetworkManager 的威力，但是安装 openSUSE 时却没有选择 wicked，直到我打开 YaST 的网络管理模块，才发现\ *膝盖中了一箭*\ 功能受限，果断切换到 wicked，从此告别抽风式断网。

在 SLES 的文档中，有这样一段。

  NetworkManager is only supported by SUSE for desktop workloads with SLED or the Workstation extension. All server certifications are done with wicked as the network configuration tool, and using NetworkManager may invalidate them. NetworkManager is not supported by SUSE for server workloads.

SUSE 只支持 NetworkManager 用于带有 SLED 或工作站扩展的桌面工作场景。所有服务器认证均是在以 wicked 为网络配置工具的情况下测试通过的，使用 NetworkManager 可能会让认证失效。SUSE 不支持 NetworkManager 用于服务器工作场景。

.. _kvm-1:

6.1 KVM
-------

在 Leap 15.2 中，允许虚拟机流量通过桥接网卡有内核参数和物理设备扩展（physdev）两种配置方式。而在 Leap 15.3 中，由于 firewalld 版本由此前 15.2 的 0.5.5 更新到 0.9.3，配置变得更加简单了，只需要把网卡添加到 firewalld 的\ ``libvirt``\ 区域（zone）即可。

6.1.1 内核参数
^^^^^^^^^^^^^^^^

第一种方法是修改内核参数，禁用桥接上的 netfilter 功能。在\ ``/etc/systl.conf``\ 中添加如下内容的文件\ ``99-disable-bridge-nf.ini``\ 。

.. code-block:: ini

   net.bridge.bridge-nf-call-ip6tables = 0
   net.bridge.bridge-nf-call-iptables = 0
   net.bridge.bridge-nf-call-arptables = 0

用\ ``sysctl``\ 命令重新加载内核参数，即可生效。

::

   # sysctl -p /etc/sysctl.conf

6.1.2 物理设备扩展
^^^^^^^^^^^^^^^^^^^^

第二种方法就是利用 netfilter 的\ ``physdev``\ 扩展。运行如下命令，确认扩展存在。

::

   $ ls /lib/modules/`uname -r`/kernel/net/netfilter/ | grep physdev
   xt_physdev.ko.xz

因为 openSUSE 自带了 firewalld，那么就不再直接用\ ``iptables``\ 命令操作，而是让 firewalld 来管理\ ``iptables``\ 规则。这里用到了\ ``firewall-cmd``\ 的\ ``--direct``\ 参数调用\ ``physdev``\ 扩展，随后重新加载规则。

::

   # firewall-cmd --permanent --direct --add-rule ipv4 filter FORWARD 0 -m physdev --physdev-is-bridged -j ACCEPT 
   # firewall-cmd --reload

其中\ ``--physdev-is-bridged``\ 用于匹配未路由的桥接流量，这个参数只在\ ``FORWARD``\ 和\ ``POSTROUTING``\ 链中有效。关于\ ``physdev``\ 扩展的更多操作见\ ``iptables``\ 文档中的\ `相应部分 <https://ipset.netfilter.org/iptables-extensions.man.html>`_\ 。

6.1.3 libvirt 区域
^^^^^^^^^^^^^^^^^^^^

根据 `libvirt 文档 <https://libvirt.org/firewall.html>`__\ ，在 libvirt 5.1.0 之前还不支持\ ``libvirt``\ 区域，而且在 firewalld 发布 0.7.0 版本之前，操作\ ``libvirt``\ 区域的功能实现一直存在问题。

所以在 Leap 15.2 中，firewalld 版本只有 0.5.5，就不需要设置网卡所属的区域。而在 Leap 15.3 中，只需要把桥接网卡添加到\ ``libvirt``\ 区域即可放行桥接流量。操作命令如下。

::

   # firewall-cmd --permanent --add-interface br0 --zone=libvirt
   # firewall-cmd --reload

另外，也可以在 YaST 中直接设置网卡所属的区域。

7. 结语
=======

openSUSE 真香！
