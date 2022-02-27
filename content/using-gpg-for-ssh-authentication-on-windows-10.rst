在 Windows 10 上用 GPG 完成 SSH 认证
####################################
:date: 2021-08-01 18:03
:author: yinian
:category: Uncategoried
:tags: GnuPG, SSH, 密钥
:slug: using-gpg-for-ssh-authentication-on-windows-10
:status: published
:feature: /images/2021/pexels-infinity-shutter-4021565.jpg
:abstract: 在《GnuPG密钥生成三步走》中，我们生成了一个用于“身份验证（Authentication）”的独立子密钥，这个子密钥可以代替 SSH 密钥，完成 SSH 认证

前言
----

在\ `《GnuPG密钥生成三步走》 <https://lab.jinkan.org/2020/04/30/gnupg-in-three-steps/>`__\ 中，我们生成了一个用于“身份验证（Authentication）”的独立子密钥，这个子密钥可以代替 SSH 密钥，完成 SSH 认证。

1. 安装 Gpg4win
---------------

首先，访问 Gpg4win 的官方网站，在\ `下载页面 <https://gpg4win.org/get-gpg4win.html>`__\ 处下载 Gpg4win。

安装时，在“选择组件”页面勾选“GPA”功能，以方便后续操作。

.. image:: /images/2021/gpg4win-install.jpg

2. 配置 Gpg4win
---------------

安装好 Gpg4win 之后，通过图形界面或者命令行导入之前生成的 GPG 密钥。

.. code-block:: powershell

   PS C:\> gpg --import marisa.keys

导入成功后，进入编辑模式，以设置密钥信任等级为“绝对（Ultimate）”。

.. code-block:: powershell

   PS C:\> gpg --edit-key marisa@jinkan.org

在编辑模式下输入\ ``trust``\ 命令，并选择\ ``5 = I trust ultimately``\ ，并通过 ``y`` 确认更改信任等级。


.. code-block:: none

   gpg> trust

   Please decide how far you trust this user to correctly verify other users' keys
   (by looking at passports, checking fingerprints from different sources, etc.)

     1 = I don't know or won't say
     2 = I do NOT trust
     3 = I trust marginally
     4 = I trust fully
     5 = I trust ultimately
     m = back to the main menu

   Your decision? 5
   Do you really want to set this key to ultimate trust? (y/N) y

运行如下命令，获取“身份验证（Authentication）”独立子密钥的 KeyGrip。

.. code-block:: none

   PS C:\> gpg -K --with-keygrip
   sec#  rsa4096 2020-03-04 [C]
         7046C3E8C8DD73F814FDE289E6ED69D1C9149F9B
         Keygrip = <40位10进制表示>
   uid           [ultimate] yinian <yinian@jinkan.org>
   ssb   ed25519 2020-03-04 [S] [expires: 2023-03-04]
         Keygrip = <40位10进制表示>
   ssb   cv25519 2020-03-04 [E] [expires: 2023-03-04]
         Keygrip = <40位10进制表示>
   ssb   ed25519 2020-03-04 [A] [expires: 2023-03-04]
         Keygrip = <40位10进制表示>

复制以\ ``[A]``\ 为标识的“身份验证（Authentication）”独立子密钥的 KeyGrip，添加到\ ``%APPDATA\gnupg\sshcontrol``\ 文件中，在注释之后另起一行。

之后需要启用 GPG 的 Putty 支持，有两种方法。一种通过 GPA 的图形界面配置，另一种则是手写配置文件。

**图形界面操作**

打开 GPA，点击\ ``Edit``\ 菜单中的\ ``Backend Preferences``\ 选项。在弹出的窗口右上角下拉菜单中选择\ ``Expert``\ 选项，之后窗口中会出现更多的配置项。勾选其中的\ ``enable-putty-support``\ 选项。

.. image:: /images/2021/gpa-configuration.jpg

**配置文件**

在\ ``%APPDATA%\gnupg\gpg-agent.conf``\ 中插入一行。

.. code-block:: ini

   enable-putty-support

做好上述配置之后，重启\ ``gpg-agent``\ 使其生效。

.. code-block:: powershell

   PS C:\> gpg-connect-agent killagent /bye
   OK closing connection

   PS C:\> gpg-connect-agent /bye
   gpg-connect-agent: no running gpg-agent - starting 'C:\Program Files (x86)\Gpg4win\..\GnuPG\bin\gpg-agent.exe'
   gpg-connect-agent: waiting for the agent to come up ... (5s)
   gpg-connect-agent: connection to agent established

至此为止，我们启用了 Gpg4Win 中的 Putty 支持，即让\ ``gpg-agent``\ 兼容\ ``pagent``\ 的行为，但这并不能与 Windows 10 自带的 OpenSSH 交互，还需要把\ ``pagent``\ 的接口包装成命名管道。

3. wsl-ssh-pageant
------------------

项目地址：\ https://github.com/benpye/wsl-ssh-pageant

该项目是用 Go 编写的，能把\ ``pagent``\ 的共享内存接口封装成了命名管道。

访问该项目的\ `下载页面 <https://github.com/benpye/wsl-ssh-pageant/releases/latest>`__\ ，下载其中的\ ``wsl-ssh-pageant-amd64-gui.exe``\ 文件，放置在一个合适的地方。根据项目说明，\ ``gui``\ 后缀不是指有实际的图形界面，而是不会弹出命令提示符窗口，适用于配置开机启动。

运行\ ``wsl-ssh-pageant``\ ，以放置在\ ``C:\Tools``\ 为例。

.. code-block:: powershell


   PS C:\Tools> wsl-ssh-pageant-amd64-gui.exe --systray --winssh ssh-pageant

其中\ ``--systray``\ 参数用于显示托盘图标，方便退出\ ``wsl-ssh-pageant``\ 。而\ ``--winssh``\ 指定\ ``wsl-ssh-pageant``\ 用于配合 Windows 自带的 OpenSSH，且命名管道名称为\ ``ssh-pageant``\ 。

.. code-block:: powershell

   PS C:\Tools> ./wsl-ssh-pageant-amd64-gui.exe --systray --winssh ssh-pageant

设置环境变量\ ``SSH_AUTH_SOCK``\ ，让\ ``wsl-ssh-pageant``\ 的命名管道作为 Windows 自带 OpenSSH 的认证代理（agent）。

.. code-block:: powershell

   PS C:\Tools> $Env:SSH_AUTH_SOCK="\\.\pipe\ssh-pageant"

然后用\ ``ssh-add``\ 访问认证代理，确认能读取到配置好的公钥。

.. code-block:: powershell

   PS C:\Tools> ssh-add -L
   ssh-ed25519 <神秘代码> (none)

用\ ``gpg``\ 导出 SSH 公钥对照是否一致。

.. code-block:: powershell

   PS C:\Tools> gpg --export-ssh-key marisa@jinkan.org
   ssh-ed25519 <神秘代码> openpgp:0xD9BA06D2

``ssh``\ 连接远程服务器，会弹出提示输入 GPG 密钥的密码（passphrase），则配置成功。

.. image:: /images/2021/pinentry-passphrase.jpg

4. 一劳永逸的开机自启动
-----------------------

前文所述的\ ``gpg-agent``\ 、\ ``wsl-ssh-pageant``\ 需要每次开机手工启动，环境变量则是每次重新打开 PowerShell 或命令提示符都需要重新配置，效果并不理想。下面通过一小段 PowerShell，写入系统环境变量，调用任务计划程序完成每次开机后的自启动。

.. code-block:: powershell

   # 设置环境变量
   [Environment]::SetEnvironmentVariable('SSH_AUTH_SOCK', '\\.\pipe\ssh-pageant', [EnvironmentVariableTarget]::User)

   # 设置为当前用户登入时自启动
   $user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
   $principal = New-ScheduledTaskPrincipal -LogonType Interactive -UserId $user
   $trigger = New-ScheduledTaskTrigger -AtLogOn -User $user
   $setting_set = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

   $gpg_agent = "GpgAgent"
   $gpg_agent_action = New-ScheduledTaskAction -Execute "gpg-connect-agent.exe" -Argument "/bye"
   $gpg_agent_td = New-ScheduledTask -Action $gpg_agent_action -Principal $principal -Trigger $trigger -Settings $setting_set
   Register-ScheduledTask -TaskName $gpg_agent -InputObject $gpg_agent_td
   Start-ScheduledTask -TaskName $gpg_agent

   $wsl_ssh_pagent = "WslSshPagnet"
   $wsl_ssh_pagent_action = New-ScheduledTaskAction -Execute "C:\Tools\wsl-ssh-pageant-amd64-gui.exe" -Argument "--systray --winssh ssh-pageant"
   $wsl_ssh_pagent_td = New-ScheduledTask -Action $wsl_ssh_pagent_action -Principal $principal -Trigger $trigger -Settings $setting_set
   Register-ScheduledTask -TaskName $wsl_ssh_pagent -InputObject $wsl_ssh_pagent_td
   Start-ScheduledTask -TaskName $wsl_ssh_pagent

至此，大功告成。
