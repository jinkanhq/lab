VSCode离线环境求生指南：远程SSH服务器
#####################################
:date: 2020-04-27 15:53
:author: yinian
:category: Uncategoried
:tags: SSH, Visual Studio Code
:slug: vscode-offline-remote-ssh
:status: published
:feature: /images/2020/pexels-erik-mclean-4582566-1024x683.jpg
:abstract: 离线远程机上 VSCode 服务器的安装

远程服务器安装
==============

本机可以直接联网
----------------

（参考 `VSCode 文档 <https://code.visualstudio.com/blogs/2019/10/03/remote-ssh-tips-and-tricks#_offline-remote-machine>`_ ）

启用\ ``remote.SSH.allowLocalServerDownload``\ 选项，即可先在本机下载 VSCode 服务器，然后自动通过 SCP 上传至远程机。

本机不能直接联网
----------------

(参考 `StackOverFlow <https://stackoverflow.com/questions/56671520/how-can-i-install-vscode-server-in-linux-offline>`_ )

打开 VSCode 的“帮助（Help）”菜单，点击“关于（About）”，在弹出的窗口中点击“复制（Copy）”按钮，即可得到类似下面的文本。

::

   Version: 1.42.1 (user setup)
   Commit: c47d83b293181d9be64f27ff093689e8e7aed054
   Date: 2020-02-11T14:45:59.656Z
   Electron: 6.1.6
   Chrome: 76.0.3809.146
   Node.js: 12.4.0
   V8: 7.6.303.31-electron.0
   OS: Windows_NT x64 10.0.18362

中文版为类似下面文本。

::

   版本: 1.42.1 (user setup)
   提交: c47d83b293181d9be64f27ff093689e8e7aed054
   日期: 2020-02-11T14:45:59.656Z
   Electron: 6.1.6
   Chrome: 76.0.3809.146
   Node.js: 12.4.0
   V8: 7.6.303.31-electron.0
   OS: Windows_NT x64 10.0.18362

复制其中的“提交（Commit）”字样后的ID，此时为\ ``c47d83b293181d9be64f27ff093689e8e7aed054``\ 。

假设远程机运行的是 64 位的 Linux 系统，利用之前获取的 Commit ID，输入下面的命令即可下载。

.. code:: bash

   $ commit_id=c47d83b293181d9be64f27ff093689e8e7aed054
   $ curl -sSL "https://update.code.visualstudio.com/commit:${commit_id}/server-linux-x64/stable" -o vscode-server-linux-x64.tar.gz

把下载好的\ ``vscode-server-linux-x64.tar.gz``\ 文件复制到远程机的用户主目录（home directory）中，在远程机上执行如下命令。

.. code:: bash

   $ commit_id=c47d83b293181d9be64f27ff093689e8e7aed054
   $ mkdir -p ~/.vscode-server/bin/${commit_id}
   $ tar zxvf vscode-server-linux-x64.tar.gz -C ~/.vscode-server/bin/${commit_id} --strip 1
   $ touch ~/.vscode-server/bin/${commit_id}/0

如此，就完成了离线远程机上 VSCode 服务器的安装。
