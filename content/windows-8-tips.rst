Windows 8 Tips
##############
:date: 2013-02-15 15:02
:author: yinian
:category: Uncategoried
:tags: Windows, Windows 8
:slug: windows-8-tips
:status: published

.NET Framework 3.5 离线安装
---------------------------

（参考 `Installing the .NET Framework 3.5 on Windows 8) <https://docs.microsoft.com/zh-cn/dotnet/framework/install/dotnet-35-windows-10>`__\ ）

利用安装镜像，以命令提示符（管理员）运行下面的命令（其中 x:\\ 为挂载镜像的盘符）:

.. code-block:: powershell

   Dism /online /enable-feature /featurename:NetFx3 /All /Source:x:\sources\sxs /LimitAccess

L2TP VPN
--------

#. 启用“IKE and AuthIP IPsec Keying Modules”和“IPsec Policy Agent”服务。
#. 在 Windows 防火墙中开启“入站规则”中的“路由和远程访问(L2TP-In)”。

Wireshark / WinPcap 4.1.2
-------------------------

#. 用 7zip 从 Wireshark 安装包中提取 WinPcap 4.1.2 安装程序或从官网下载。
#. 以 Windows 7 兼容模式运行 WinPcap 安装程序。
#. 选择“运行程序而不获取帮助”。

Metro 版 Internet Explorer 10 消失或失效
----------------------------------------

#. 取消“Internet 选项”中“程序”选项卡中的“IE 磁贴用于打开桌面上的 Internet Explorer”选项。
#. 把 Internet Explorer 设置为默认的浏览器

SSD 相关配置
------------

（参考 `Windows 8 SSD Settings, Etc. <http://www.tweakhound.com/2012/11/14/windows-8-ssd-settings-etc/>`__\ ）

Windows 8 会识别出 SSD，本身就提供一些优化，请注意：

-  **不要禁用**\ 磁盘整理，Windows 会对 SSD 进行 Trim。
-  **不要禁用** Superfetch 或 Prefetch。注册表默认没有EnableSuperfetch一项：

.. code-block:: registry

   [HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters]
   "EnablePrefetcher"=dword:00000003
   "EnableBootTrace"=dword:00000000

Intel SSD Toolbox 指出：

   在 Windows Vista 和 Windows 7 中，Superfetch 跟踪那些最常用的文件并复制到内存来缩短加载速度。Superfetch 基于 Windows XP 中类似的 Prefetch 功能。在 Intel SSD 上的 Windows 7 或 Windows Vista 中，应禁用 Superfetch/Prefetch 功能来获得最佳性能。在 Windows 8 中，Superfetch 的功能与之前版本中的有所不同，不应在 Intel SSD 上禁用。

-  禁用 Windows Search 服务。
-  （可选）用 powercfg -h off 禁用休眠。
-  （可选）禁用系统保护。
-  （可选）禁用页面文件。
