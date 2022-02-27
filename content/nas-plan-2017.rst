NAS 方案  (2017)
################
:date: 2017-04-23 16:07
:author: yinian
:category: Uncategoried
:tags: Intel, MegaRAID, Seagate
:slug: nas-plan-2017
:status: published
:feature: /images/2017/silver-hard-drive-interals-33278.jpg
:abstract: 本次折腾可谓一波三折，不过也实现了多年的愿望，自己组建了一台还性能不错的 NAS。下面整理了本次折腾中踩的坑，以供维护参考

本次折腾可谓一波三折，不过也实现了多年的愿望，自己组建了一台还性能不错的 NAS。下面整理了本次折腾中踩的坑，以供维护参考。

本次硬件配置如下：

+------------+------------------------------------+--------+----------------------------+
| 类别       | 型号                               | 数量   | 备注                       |
+============+====================================+========+============================+
| CPU        | Intel Pentium G4560                | 1      | 散片                       |
+------------+------------------------------------+--------+----------------------------+
| 主板       | ASRock B250M Pro4                  | 1      | M-ATX                      |
+------------+------------------------------------+--------+----------------------------+
| 内存       | Kingston HyperX Fury 8GB DDR4-2400 | 1      |                            |
+------------+------------------------------------+--------+----------------------------+
| RAID控制器 | IBM ServeRAID M5015                | 1      | LSI MegaRAID 9260-8i       |
+------------+------------------------------------+--------+----------------------------+
| 硬盘       | Seagate ST4000NM0035               | 4      | Enterprise Capacity 7200.5 |
+------------+------------------------------------+--------+----------------------------+
| 机箱       | Fractal Design Node 804            | 1      | M-ATX/双箱体/8个3.5寸盘位  |
+------------+------------------------------------+--------+----------------------------+
| 电源       | Seasonic G-450                     | 1      | 半模组/80 PlUS Gold        |
+------------+------------------------------------+--------+----------------------------+

安装系统为 Windows Server 2016，用 Hyper-V 虚拟化一台 CentOS 7 直接挂载 RAID5 裸盘，采用 XFS。

Intel I219-V 驱动
====================

根据 Intel 的\ `产品简介 <http://www.intel.com/content/www/us/en/embedded/products/networking/ethernet-connection-i219-family-product-brief.html>`_\ ，I219-V 和 I219-LM 的差异只有三项：vPro 支持、SIPP 支持和服务器操作系统支持。可以理解为只有驱动上有区别，实际硬件功能相等。而在 Windows Server 2016 中，通过 Intel 提供的驱动程序并不能安装 I219-V 的驱动，并提示没有支持的网卡。

|image1|

Seagate Enterprise Capacity 7200.5
=========================================

我这次选购的硬盘型号为希捷企业级 7200 转 SATA 盘的第五代产品，容量 4T，扇区格式 512n，出厂时固件版本 TN02。上机之后工作时发出有规律异响，振动较大。经 `Chiphell 上一帖子 <https://www.chiphell.com/thread-1717406-1-1.html>`_\ 提示，更新希捷官方 2017 年 2 月发布的新固件 TNC2，工作时状态恢复至正常水平。

**固件下载**

`ST4000NM0035 1V4107 TNC2@百度网盘 <https://pan.baidu.com/s/1o8iBcvC/>`_

神秘代码：\ ``bwj3``

通过 StorCLI 更新硬盘固件
----------------------------

我的 4 块硬盘都接在 RAID 控制卡上，Seagate 提供的固件升级工具无法识别硬盘，可使用StorCLI 更新固件。

.. code-block:: bash

   # 确认控制器序号
   storcli show
   # 确认磁盘柜编号和磁盘槽编号。其中 x 为编号（例如：控制器 0 则为 /c0）
   storcli /cx/eall/sall show
   # 更新指定磁盘的固件。执行完成需额外等待一段时间再执行下一磁盘的更新，否则下一磁盘固件
   # 更新会失败，在 RAID 控制器日志中报 Microcode update failed 警报。
   storcli /cx/ex/sx download src=/path/to/fireware.lod

StorCLI 下载
---------------

`v1.21.16@百度网盘 <https://pan.baidu.com/s/1mihZiRm/>`_

神秘代码：\ ``xgzd``

文件系统
===========

因为存在一些合集档路径长度超出 Windows 中 ``MAX_PATH`` 的 255 个字符限制，因此实际存储的文件系统选择了 CentOS 7 默认配备的 XFS。

在执行 ``mkfs.xfs`` 时，需匹配阵列实际参数以优化性能。

XFS 在 RAID 上的优化
-----------------------

（参照 `XFS FAQ <https://xfs.org/index.php/XFS_FAQ#Q:_How_to_calculate_the_correct_sunit.2Cswidth_values_for_optimal_performance>`__\ ）

XFS 支持在挂载参数上针对给定的 RAID 条带单元（条带大小）和条带宽度（数据磁盘的数目）调优。

有些情况下，这些参数可以自动检测，不过对大多数硬件 RAID 仍然需要手动计算这些参数。

计算这几个参数值很简单：

.. code-block:: ini

   su = <RAID 控制器条带大小，单位是字节（或以 KB 计量单位，以 k 结尾）
   sw = <数据磁盘的数目（不包含奇偶校验盘）>

那么，如果你的 RAID 控制器条带大小是 64KB，并且已经配置好 8 块磁盘的 RAID-6：

.. code-block:: ini

   su = 64k
   sw = 6

RAID 条带 256KB 的 16 块磁盘的 RAID-10：

.. code-block:: ini

   su = 256k
   sw = 8

此外，你也可以用\ ``sunit``\ 和\ ``swidth``\ 代替\ ``su``\ 和\ ``sw``\ ，此时单位是 512B 扇区的个数。

注意，\ ``xfs_info``\ 和\ ``mkfs.xfs``\ 会把\ ``sunit``\ 和\ ``switch``\ 按 512B 扇区的个数解释，但在报告时却以\ ``bsize``\ 为单位。

假设这样的例子：执行\ ``mkfs.xfs``\ 指定\ ``swidth``\ 为 1024，\ ``bsize``\ 为 4096，\ ``mkfs.xfs``\ 执行结果显示\ ``swidth``\ 为 128。128 x 4096 == 1024 x 512。

在硬件 RAID 上的 LVM 中创建 XFS 时，使用与在硬件 RAID 上直接创建 XFS 时一样的\ ``sunit``\ 和\ ``swidth``\ 参数。

现状（2020）
===============

现已升级到 i5-7500T、512G NVMe SSD、32G 内存。常驻 3 台虚拟机：

-  存储：CentOS 7，提供内网 SMB、NextCloud 服务。
-  下载机：Windows 7，百度云、115、迅雷下载。
-  沙盒：蜜汁操作。

.. |image1| image:: /images/2017/i219v-i219lm-comparision.jpg
