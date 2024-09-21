用 WSL2 实现家庭梦想一起 ROCm
################################
:date: 2024-09-20 22:40
:author: yinian
:category: Uncategoried
:tags: WSL2, ROCm, AMD, Ubuntu
:slug: wsl2-realizes-family-dreams-together-with-rocm
:status: published
:feature: /images/2024/pexels-nicolas-foster-65973708-20031379.jpg
:abstract: AMD？这不是玩游戏的吧？咱们家是要建火箭还是要开矿啊


.. role:: strike
   :class: strike


.. attention::

   本文内容仅适用于以下桌面端型号显卡，所有移动端型号均不在支持范围内：\
   [rocm-doc-wsl-compatibility]_

   * AMD Radeon RX 7900 XTX
   * AMD Radeon RX 7900 XT
   * AMD Radeon RX 7900 GRE
   * AMD Radeon PRO W7900
   * AMD Radeon PRO W7900DS
   * AMD Radeon PRO W7800

前言
==========

由于笔者家境贫寒，苦于 NVIDIA 显卡价格居高不下，只能退求其次选择了 24GB 显存的
AMD Radeon RX 7900XTX，并在双系统 Ubuntu 22.04 LTS 跑起 ROCm，在泥巴地中欢快地\
打滚，同画面撕裂和 ALC887 斗智斗勇，跑通了 LLM、Stable Diffusion、ComfyUI 多种\
任务，直到 AMD 于 2024 年 6 月 27 日发布了肾上腺素（Adrenalin）驱动 24.6.1 版\
本。

.. admonition:: 喜报！

   正式支持 ROCm 在 Windows Subsystem for Linux 2（以下简称“WSL2”）上运行。\
   自此可以免去维护 Ubuntu 和 Windows 双系统启动了，直接在 WSL2 中就可以运行
   ONNXRuntime 和 PyTorch 任务了。\ :strike:`正式加入了 Counter-Strike 2 的 Anti-Lag 2 支持，不再有被判作弊风险了。`

   望周知。


尽管在众多 WSL2 分发版中，仅支持 Ubuntu 22.04 和 5.15 内核，但问题也变得简单\
多了，可以按照经典的三步走来操作。

1. 打开 Ubuntu 22.04 LTS 的 WSL2 分发版；
2. 在 WSL2 中安装 ROCm；
3. \ :strike:`把 WSL2 门关上`\  安装 ONNXRuntime 和 PyTorch 等负载运行环境。


1. 准备 WSL2
================

.. attention::

    请确认已安装好肾上腺素（Adrenalin）驱动，且版本高于 24.6.1。

在 CMD 或 PowerShell 中输入以下命令安装即可：

.. code-block:: powershell

   wsl --install -d Ubuntu-22.04

进入 WSL2 的 Shell，更新系统包确认 WSL2 的分发版和内核版本：

.. code-block:: console

   $ lsb_release -a
   No LSB modules are available.
   Distributor ID: Ubuntu
   Description:    Ubuntu 22.04.5 LTS
   Release:        22.04
   Codename:       jammy
   $ uname -r
   5.15.153.1-microsoft-standard-WSL2

2. 安装 ROCm
====================

首先，保持更新系统包的良好习惯。

.. code-block:: console

   $ sudo apt update && sudo apt upgrade -y

通过 ``amdgpu-install`` 工具来安装一揽子 ROCm 组件，而不必手动指定各个组件的软\
件包名，以简化安装过程。此外，该工具还提供了一键卸载 ROCm 软件栈的功能。

.. code-block:: console

    $ wget https://repo.radeon.com/amdgpu-install/6.1.3/ubuntu/jammy/\
    amdgpu-install_6.1.60103-1_all.deb
    $ sudo apt install ./amdgpu-install_6.1.60103-1_all.deb

通过指定 ``--usecase`` 参数，可以选择性安装 WSL2 环境的 ROCm 组件。另外，还要指\
定 ``--no-dkms`` 参数，表示不启用 DKMS（Dynamic Kernel Module Support，动态内\
核模块支持）。

.. code-block:: console

    $ amdgpu-install -y --usecase=wsl,rocm --no-dkms

该安装工具会在 ``/etc/apt/sources.list.d`` 中留下 ``amdgpu.list`` 和
``rocm.list`` 等文件，用来管理 Ubuntu 中的 AMD 显卡驱动和 ROCm 的软件源。这些\
软件源是 AMD 提供的，均位于 ``https://repo.radeon.com`` 域名下，在安装过程中需\
要保证合理的网络环境。

尽管在本文完成之时，ROCm 的最新版本为 6.2.0，但目前仅 ROCm 6.1.3 版本对应的\
AMD 显卡 Linux 驱动（修订号 24.10.3）仓库中包含了 WSL2 支持所需的
两个 deb 包：\ ``hsa-runtime-rocr4wsl-amdgpu`` 和 ``rocminfo4wsl-amdgpu`` 。

前者为 AMD 实现的异构系统架构（Heterogeneous System Architecture，HSA）运行时，\
也称 ROCm 运行时（ROCR），提供直接利用 AMD 显卡计算能力的用户态 API。

后者为 ``rocminfo`` 工具，用于报告系统信息，可枚举工作 ROCm 栈中的 GPU 代理\
（agents）。


.. note::

    吊诡的是, ROCm 的发布历史中并没有列出 6.1.3 版本，仅在 WSL 相关文档页面\
    提及此版本的存在，而发布历史中列出的最新版本 6.2.0 仓库中却缺少上述两个关键\
    deb 包 。\ [rocm-doc-release-history]_

.. note::

    此外，从上述两个 deb 包 ``/usr/share/doc/`` 目录存放的变更历史信息中可\
    以看出，构建这两个包的源码来自 ``gerritgit/release/rocm-rel-6.1`` 分支，由\
    AMD 自动构建系统发布，且在 Github 上官方仓库中也找不到对应的源码，疑似为闭\
    源内容。


3. 安装负载运行环境
=======================

在 AMD 的软件源中，同样可以找到一些 ROCm 官方提供的负载运行环境，如 PyTorch、\
ONNXRuntime 等，可以直接通过指定 URL 的方式安装。

3.1 PyTorch
-----------------

可以从 PyTorch 官方源安装对应 ROCm 6.1 的 ``whl`` 包，\ ``torch`` 最新版本为
2.4.1。

.. code-block:: console

   $ pip install torch torchvision torchaudio --index-url \
   https://download.pytorch.org/whl/rocm6.1


也可以通过 AMD 的官方源安装，但仅支持 Python 3.10，且 \ ``torch`` 和
``torchvision`` 的版本分别为 2.1.2 和 0.16.1。

.. code-block:: console

   $ pip install torch torchvision --index-url \
   https://repo.radeon.com/rocm/manylinux/rocm-rel-6.1.3/


安装后用 ``hsa-runtime-rocr4wsl-amdgpu`` 包提供的 ``libhas-runtime64.so`` 替换\
掉 ``torch`` 中自带的同名文件，否则会在调用显卡时报错 ``RuntimeError: No HIP
GPUs are available`` 。\ [rocm-doc-limitions]_

.. code-block:: console

   $ location=`pip show torch | grep Location | awk -F ": " '{print $2}'`
   $ rm ${location}/torch/lib/libhsa-runtime64.so*
   $ ln -s /opt/rocm/lib/libhsa-runtime64.so.1.2 ${location}/libhsa-runtime64.so


安装后可通过 ``torch.cuda`` 模块验证能否正常检测到 AMD 显卡。

.. code-block:: python

   >>> import torch
   >>> torch.cuda.is_available()
   True
   >>> torch.cuda.get_device_name(0)
   'AMD Radeon RX 7900 XTX'


3.2 ONNXRuntime
-------------------

.. admonition:: 悲报！

   微软没有发布过带有 ROCm 支持的 ONNXRuntime 二进制 ``whl`` 分发包。

   望周知。

.. note::

   虽然在 PyPI 中可以找到一个叫 ``onnxruntime-gpu`` 的包，但这个包徒有其名，仅\
   包含 CUDA 支持。尽管在 https://download.onnxruntime.ai/ 中可以找到用于训练的
   ONNXRuntime 包，但支持的 ROCm 版本很低。


如果不想从源码编译安装，畅享 1 小时以上的\ :strike:`摸鱼`\ 编译时间，也可以从 
AMD 的官方源安装，但仅支持 Python 3.10，且包版本为 1.17.0。

通过 ``pip`` 的 ``--index-url`` 参数指定 AMD 的官方源安装会遇到 ``Could not
find a version that satisfies the requirement`` 报错。

原因是在 AMD 提供的 ONNXRuntime 二进制 ``whl`` 分发包元信息中，实际的分发包名称
为 ``onnxruntime-rocm`` ，但 ``whl`` 文件名中对应分发包名称的部分是 
``onnxruntime_rocm``\ ，一字之差即与 Python 打包规范先进工作者失之交臂。

只能迂回一下，直接指定 ``whl`` 包的 URL 来安装。

.. code-block:: console

   $ pip install https://repo.radeon.com/rocm/manylinux/rocm-rel-6.1.3/\
   onnxruntime_rocm-1.17.0-cp310-cp310-linux_x86_64.whl

之后，还要手动降级 ``numpy`` 版本，否则会报错。

.. code-block:: console

   $ pip install "numpy<2"

最后，验证能否识别到 ROCm 的 ``ExecutionProvider`` 。

.. code-block:: python

   >>> import onnxruntime as ort
   >>> ort.get_available_providers()
   ['MIGraphXExecutionProvider', 'ROCMExecutionProvider', 'CPUExecutionProvider']

推断负载的运行测试可参照 ONNXRuntime 的\ `官方样例代码 <https://github.com/
microsoft/onnxruntime-inference-examples/tree/main/python>`_\ ，并把其中涉及
``ExecutionProvider`` 的部分修改成 ``ROCMExecutionProvider`` 即可。

3.3 llama.cpp
-------------------

从 https://github.com/ggerganov/llama.cpp/releases 下载最新版本的 llama.cpp 源\
码，解压后进入目录开始编译 ROCm 支持。

.. code-block:: console

   $ cd llama.cpp-b3798
   $ make -j GGML_HIPBLAS=1 AMDGPU_TARGETS=gfx1100

其中 ``AMDGPU_TARGETS`` 参数的值可以从 ``rocminfo`` 取得。

.. code-block:: console

   $ rocminfo | grep gfx | head -1 | awk '{print $2}'
   gfx1100

在编译完成后，用 ``llama-bench`` 工具验证是否可用并测试性能。下面的例子中使用\
了 ``qwen2`` 系列模型。

.. code-block:: console

   $ ./llama-bench -m ~/qwen2-7b-instruct-q4_0.gguf -ngl 29
   ggml_cuda_init: GGML_CUDA_FORCE_MMQ:    no
   ggml_cuda_init: GGML_CUDA_FORCE_CUBLAS: no
   ggml_cuda_init: found 1 ROCm devices:
     Device 0: AMD Radeon RX 7900 XTX, compute capability 11.0, VMM: no
   | model                          |       size |     params | backend    | ngl |          test |                  t/s |
   | ------------------------------ | ---------: | ---------: | ---------- | --: | ------------: | -------------------: |
   | qwen2 ?B Q4_0                  |   4.13 GiB |     7.62 B | ROCm       |  29 |         pp512 |      3605.67 ± 56.61 |
   | qwen2 ?B Q4_0                  |   4.13 GiB |     7.62 B | ROCm       |  29 |         tg128 |         92.45 ± 1.54 |

实测结果显示，WSL2 下的 ``llama.cpp`` 与 Native Linux 下的性能无明显差异。

4. 结语
=============

笔者作为一名 AMD Radeon RX 7900XTX 用户，在经历了被迫手动编译 ONNXRuntime 等\
等一系列麻烦后，只剩下了赞美。

24GB + 122.8 TFLOPS（FP16）就是便宜大碗！


.. [rocm-doc-wsl-compatibility] ROCm Documentation: `Compatibility matrices
   (WSL) <https://rocm.docs.amd.com/projects/radeon/en/latest/docs/
   compatibility/wsl/wsl_compatibility.html>`_

.. [rocm-doc-release-history] ROCm Documentation: `ROCm release history
   <https://rocm.docs.amd.com/en/latest/release/versions.html>`_

.. [rocm-doc-limitions] ROCm Documentation: `Limitations and recommended
   settings <https://rocm.docs.amd.com/projects/radeon/en/latest/docs/
   limitations.html>`_
