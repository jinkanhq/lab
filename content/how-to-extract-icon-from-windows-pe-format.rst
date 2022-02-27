考古：Windows 文件图标与其提取方法
####################################
:date: 2022-02-27 16:42
:author: yinian
:category: Uncategoried
:tags: Windows, Icon, Python, pywin32
:slug: how-to-extract-icon-from-windows-pe-format
:status: published
:feature: /images/2022/pexels-denis-zagorodniuc-3449662.jpg
:abstract: 如何程序化提取 Windows 下文件的图标，其实是一个考古问题

前言
==========

数个月前，笔者用心爱的 Python 酝酿着一个名为“Smoothie”的跨平台文件浏览器（至今\
仍在难产，暂未发布），为了在 Windows 下显示与 ``explorer.exe`` 中一致的文件图\
标，不得不在 Win32 的历史包袱中摸索解决方法。本文记录了这部分考古工作，并给一\
些“历史文件”做了备份。要从 Windows 下的文件提取图标，保存成图像，首先要从 PE 格\
式讲起。


1. 可移植的可执行文件（PE）格式
====================================

可移植的可执行文件（PE，Portable Executable）从\ `通用目标文件格式
<https://en.wikipedia.org/wiki/COFF>`_\（COFF，Common Object File Format）衍生\
而来，“可移植的”这一修饰语，意为这些可执行文件可在所有版本的 Windows 及其支持的
CPU 上运行。可执行程序（EXE，Executable Program）动态链接库（DLL，Dynamic Link
Library）都是相同的 PE 格式，以一个比特区别开来，仅在语义上有所区分，而且动态链\
接库文件的后缀名也没有限定，例如 OLE 控件扩展（OCX，OLE Control Extension）和控\
制面板程序（CPL，Control Panel Applets）其实都是动态链接库。更多关于 PE 格式的\
细节与历史沿革见 [MSDN-Magazine-Feb-2002]_\ 。

在 PE 文件中，节（Section）是表示代码或数据的最小单位，类似于 Intel 8086 架构的\
段（Segment）。其中的 ``.rsrc`` 节用于存放资源（Resource），文件图标即是一种资\
源，存放在这一节。\ ``.rsrc`` 节的解析方法见 [MSDN-Win32-Debug-rsrc]_\ 。

直接上手解析二进制格式未免太过复杂与繁琐，可谓是“从入门到放弃”，笔者转而投向了\
能解析 PE 格式并读取资源的 Win32 API。因为笔者的项目是用 Python 编写的，本文中\
示例代码均调用 pywin32 封装过的 Win32 API，与微软官方示例的 C++ 代码会有所出入。


2. 图标资源
===============

资源（Resource）是 Windows 应用中的二进制数据（区别于可执行代码），标准化的资\
源包括图标（Icon）、鼠标指针（Cursor）、字体（Font）、位图（Bitmap）等等。单个\
图标的资源类型是 ``RT_ICON`` ，而最常见的包含多种大小、颜色位深、图像格式的图标\
则是 ``RT_ICON_GROUP`` 类型。这两个常量的值可以在 ``winuser.h`` 中找到。

读取图标的任务可以用读取资源的一系列 API 搭配完成，另外还需要做一些异常处理。首\
先加载 PE 文件，因为这里只关心图标资源，所以用指定了
``LOAD_LIBRARY_AS_DATA_FILE`` 参数的 ``LoadLibraryEx`` 函数，这样系统会把 PE 文\
件加载为数据文件。

.. code-block:: python

    import pywintypes
    import win32api
    import win32con
    import winerror
    from typing import Union, Iterator

    def load_library_as_datafile(library_path: str):
        library_handle = win32api.LoadLibraryEx(library_path, 0, LOAD_LIBRARY_AS_DATAFILE)
        assert library_handle != 0
        return library_handle

加载成功后会获得一个句柄（Handle），接下来通过这个句柄枚举 PE 文件中的所有图标\
资源。这里用到了 ``EnumResourceNames`` 函数枚举资源名称，并用 ``RT_GROUP_ICON``\
制定枚举的资源类型为图标。

.. code-block:: python

    library_handle = load_library_as_datafile("/lab-jinkan-org.exe")
    group_icon_resource_names = win32api.EnumResourceNames(
        library_handle, win32con.RT_GROUP_ICON
    )

通过 ``LoadResource`` 函数按资源名称加载图标资源。

.. code-block:: python

    resouce_name = group_icon_resource_names[0]
    try:
        resource = win32api.LoadResource(
            library_handle, win32con.RT_GROUP_ICON, resource_name
        )
    except pywintypes.error as e:
        if e.winerror != winerror.ERROR_RESOURCE_NAME_NOT_FOUND:
            raise e
        else:
            return b""

以加载第一个图标为例，若遇到资源不存在的异常则返回空字节串，其他异常则继续抛\
出。此处用到的 ``win32api.LoadResource`` 函数是 pywin32 封装好的，包含了\
``FindResourceEx``\ 、\ ``SizeofResource``\、 \ ``LoadResource``\ 以及
``LockResource``\ 一揽子操作\ [1]_\ ，并包装了异常处理，详情见源码\
[pywin32-win32apimodule-L5227]_\ 。

至此，我们已经可以从 PE 文件中加载图标资源，但资源中的图标格式与 ``.ICO`` 文件\
的格式不尽相同，还需要额外的转换工作。

3. 图标格式
===============

Windows 中的图标有两种格式：图标资源 ``RT_GROUP_ICON`` 格式与图标文件 ``.ICO``\
格式。本节会分别介绍两种格式和转换方法。


3.1 RT_GROUP_ICON 格式
----------------------------

通过 ``win32api.LoadResource`` 加载的 ``RT_GROUP_ICON`` 其实是一个
``GRPICONDIR`` 结构体。

.. code-block:: cpp

    typedef struct 
    {
        WORD              idReserved;     // 保留字段，必须为 0
        WORD              idType;         // 资源类型（图标为 1）
        WORD              idCount;        // 图标中的图像数量
        GRPICONDIRENTRY   idEntries[1];   // 每个图像对应的条目（Entry）
    } GRPICONDIR, *LPGRPICONDIR;

在这个结构体中，值得关注的是 ``idCount`` 和 ``idEntries`` 成员。前者表示图标资\
源中的图像（Image）数量，即条目数组 ``idEntries`` 的长度。\ ``idEntries`` 中的\
每个条目表示图标中的一个图像。表示条目的结构体 ``GRPICONDIRENTRY`` 如下所示。

.. code-block:: cpp

    typedef struct
    {
        BYTE   bWidth;               // 图像的宽度，单位为像素
        BYTE   bHeight;              // 图像的高度，单位为像素
        BYTE   bColorCount;          // 图像中的颜色数量 （如果多于 8 位深则为 0）
        BYTE   bReserved;            // 保留字段
        WORD   wPlanes;              // 色彩平面数
        WORD   wBitCount;            // 每像素位数
        DWORD  dwBytesInRes;         // 图像资源的字节数
        WORD   nID;                  // 图像资源 ID
    } GRPICONDIRENTRY, *LPGRPICONDIRENTRY;


其中，\ ``dwBytesInRes`` 成员表示整个 ``RT_ICON`` 的大小，\ ``nID`` 表示图像的
资源 ID。这个资源 ID 即可用于 \ ``FindResourceEx``\ 、\ ``SizeofResource``\ 、\
``LoadResource``\ 以及 \ ``LockResource``\ 一揽子操作，获取 ``ICONIMAGE`` 结\
构体类型的图像指针。\ ``ICONIMAGE``\ 即是 ``.ICO`` 文件中图像的格式，将在下一\
节中详细介绍。

3.2 ICO 格式
---------------

每个 ``.ICO`` 图标文件对应一个图标资源 ``RT_GROUP_ICON``\ 。图标文件中同样以目录
形式组织并存储多个图像。\ ``.ICO`` 文件中的目录以 ``ICONDIR`` 结构体表示。

.. code-block:: cpp

    typedef struct
    {
        WORD           idReserved;   // 保留字段，必须为 0
        WORD           idType;       // 资源类型（图标为 1）
        WORD           idCount;      // 图标中的图像数量
        ICONDIRENTRY   idEntries[1]; // 每个图像对应的条目（Entry）
    } ICONDIR, *LPICONDIR;

``idEntries`` 数组中的条目以 ``ICONDIRENTRY`` 结构体表示，对应图标中的各个图\
像。可以看出，\ ``ICONDIR`` 与 ``GRPICONDIR`` 几乎一模一样。

.. code-block:: cpp

    typedef struct
    {
        BYTE        bWidth;          // 图像的宽度，单位为像素
        BYTE        bHeight;         // 图像的高度，单位为像素
        BYTE        bColorCount;     // 图像中的颜色数量 （如果多于 8 位深则为 0）
        BYTE        bReserved;       // 保留字段（必须为 0）
        WORD        wPlanes;         // 色彩平面数
        WORD        wBitCount;       // 每像素位数
        DWORD       dwBytesInRes;    // 图像资源的字节数
        DWORD       dwImageOffset;   // 图像资源的偏移量
    } ICONDIRENTRY, *LPICONDIRENTRY;

可以看出，\ ``ICONDIRENTRY`` 与 ``GRPICONDIRENTRY`` 只有两个成员的差距。前者最
后一个成员是偏移量，而后者是资源 ID；前者是图像数据的大小，后者是整个
``RT_ICON`` 资源的大小。以 ``.ICO`` 文件头为起始，按偏移量 ``dwImageOffset``
可以读取到文件中存储的图像 ``ICONIMAGE``\ 。

.. code-block:: cpp

    typdef struct
    {
        BITMAPINFOHEADER   icHeader;      // DIB 头
        RGBQUAD            icColors[1];   // 颜色盘
        BYTE               icXOR[1];      // 用于异或（XOR）蒙版的 DIB 位
        BYTE               icAND[1];      // 用于与（AND）蒙版 DIB 位
    } ICONIMAGE, *LPICONIMAGE;

这个结构体中涉及了 Windows 图形设备接口（GDI，Graphics Device Interface）中的\
设备无关位图（DIB，Device Independent Bitmap）。跟随 Windows Vista 之前的文档至\
此，提取出 ``ICONIMAGE`` 后，就会遇到兼容性的断点。

在 Windows Vista 之后，\ ``.ICO`` 文件中容纳的不仅是 DIB，还有 PNG。
``ICONIMAGE`` 中的 ``icHeader`` 成员，是一个 ``BITMAPINFOHEADER`` 结构体，如果\
它的成员 ``biCompression`` 值为 ``BI_PNG``\ ，那么这个 ``ICONIMAGE`` 就是一幅\
PNG 图像，不能按 DIB 的方式来读取。

在 Python 的图像处理库 Pillow 中，有一个能读取 ``.ICO`` 文件的插件
`IcoImagePlugin <https://github.com/python-pillow/Pillow/blob/main/src/PIL/
IcoImagePlugin.py>`_\ ，它能正确处理这一差异。我们只剩下一点微小的工作，就是把\
``RT_GROUP_ICON`` 转换成 ``.ICO``\ ，然后交给 Pillow 来处理。


3.3 转换
===============

首先做一些准备工作，用 ``struct`` 模块在 Python 中重新发明上述这些结构体，计算结
构体的大小，并用 ``namedtuple`` 结构化展示，尽量避免手动操作字节串。Windows 中的
数据类型与 C 语言的基础数据类型对照关系参看\ [MSDN-Win32-WinProg-DataTypes]_\ 。

.. code-block:: python

    import struct
    from collections import namedtuple

    # ICONDIR 的前三个成员
    ICONDIR_HEADER_FORMAT = "HHH"
    ICONDIR_HEADER_SIZE = struct.calcsize(ICONDIR_HEADER_FORMAT)

    # ICONDIRENTRY
    ICONDIRENTRY_FORMAT = "BBBBHHLL"
    ICONDIRENTRY_SIZE = struct.calcsize(ICONDIRENTRY_FORMAT)
    IconDirectoryEntry = namedtuple(
        "IconDirectoryEntry",
        "bWidth,bHeight,bColorCount,bReserved,"
        "wPlanes,wBitCount,dwBytesInRes,dwImageOffset",
    )

    # GRPICONDIR 的前三个成员
    GRPICONDIR_HEADER_FORMAT = "HHH"
    GRPICONDIR_HEADER_SIZE = struct.calcsize(GRPICONDIR_HEADER_FORMAT)
    GroupIconDirectoryHeader = namedtuple(
        "GroupIconDirectoryHeader", "idReserved,idType,idCount"
    )

    # GRPICONDIRENTRY
    GRPICONDIRENTRY_FORMAT = "BBBBHHLH"
    GRPICONDIRENTRY_SIZE = struct.calcsize(GRPICONDIRENTRY_FORMAT)
    GroupIconDirectoryEntry = namedtuple(
        "GroupIconDirectoryEntry",
        "bWidth,bHeight,bColorCount,bReserved," "wPlanes,wBitCount,dwBytesInRes,nID",
    )

接第 2 节的结尾，利用 ``win32api.LoadResource`` 加载的 ``RT_GROUP_ICON`` 资源\
后，枚举其中的 ``RT_ICON``\ ，把 ``GRPICONDIRENTRY`` 逐一转换成
``ICONDIRENTRY``\ ，然后再把图像数据原封不动复制过去，按顺序计算偏移量，即可构\
造 ``.ICO`` 文件。

首先计算结构体中大小与数量的值，设置初始偏移量。

.. code-block:: python

    from io import BytesIO

    # 空缓冲区
    buffer = BytesIO()
    # 解析 GRPICONDIR 的前三个成员
    group_icon_dir_header = GroupIconDirectoryHeader._make(
        struct.unpack(GRPICONDIR_HEADER_FORMAT, resource[:GRPICONDIR_HEADER_SIZE])
    )
    icon_dir_count = group_icon_dir_header.idCount
    # 计算 ICONDIR 的大小
    icon_dir_size = ICONDIR_HEADER_SIZE + ICONDIRENTRY_SIZE * icon_dir_count
    # GRPICONDIR 与 ICONDIR 的前三个成员一致，直接复制数据
    buffer.write(resource[:ICONDIR_HEADER_SIZE])
    group_icon_dir_entries = resource[ICONDIR_HEADER_SIZE:]
    # 设置图像偏移量起始值
    offset = icon_dir_size

开始一对一的转换。

.. code-block:: python

    for i in range(icon_dir_count):
        # 确定 GRPICONDIRENTRY_ 边界
        entry_start = GRPICONDIRENTRY_SIZE * i
        entry_end = entry_start + GRPICONDIRENTRY_SIZE
        # 解析 GRPICONDIRENTRY
        group_icon_dir_entry = GroupIconDirectoryEntry._make(
            struct.unpack(
                GRPICONDIRENTRY_FORMAT, group_icon_dir_entries[entry_start:entry_end]
            )
        )
        # 按资源 ID 加载 RT_ICON 资源，返回的数据是一个 ICONIMAGE
        icon_image = win32api.LoadResource(
            library_handle, win32con.RT_ICON, group_icon_dir_entry.nID
        )
        icon_image_size = len(icon_image)
        # GRPICONDIRENTRY 与 ICONDIRENTRY 的前六个成员相同，直接复制数据
        # 只需要指定 ICONDIRENTRY 的偏移量和图像大小
        icon_dir_entry = IconDirectoryEntry(
            *group_icon_dir_entry[:6],
            dwImageOffset=offset,
            dwBytesInRes=icon_image_size
        )
        # 找到相应位置写入数据
        buffer.seek(ICONDIR_HEADER_SIZE + ICONDIRENTRY_SIZE * i)
        buffer.write(struct.pack(ICONDIRENTRY_FORMAT, *icon_dir_entry))
        buffer.seek(offset)
        buffer.write(icon_image)
        # 累计偏移量
        offset += icon_image_size

循环结束后，缓冲区中将是完整的 ``.ICO`` 文件了。剩下的工作交给 Pillow。

.. code-block:: python

    from PIL import Image
    
    buffer.seek(0)
    img = Image.open(buffer, formats=("ico",))
    img.save("jinkan-icon.png")

Pillow 默认会从 ``.ICO`` 文件中取到最大分辨率的图像，保存成指定的格式。

至此，大功告成。如果有兴趣了解更多细节，包括笔者可以绕过避之不谈的 GDI 部分，都
可以下面的引用资料中找到。


.. [1] 查找（Find）、加载（Load）、锁定（Lock）是 Windows 中加载资源的标准编程模
       型，自 16 位 Windows 时期一脉相承，扛起了 Windows 向前兼容性的历史包袱。

.. raw:: html

    <div class="divider"><div class="inner-text">引用</div></div>

.. [MSDN-Magazine-Feb-2002] Inside Windows: `An In-Depth Look into the Win32 
   Portable ExecutableFile Format <https://docs.microsoft.com/en-us/archive/
   msdn-magazine/2002/february/inside-windows-win32-portable-executable
   -file-format-in-detail>`_

.. [MSDN-Win32-Debug-rsrc] PE Format: `The .rsrc Section <https://docs.
   microsoft.com/en-us/windows/win32/debug/pe-format#the-rsrc
   -section>`_

.. [pywin32-win32apimodule-L5227] mhammond/pywin32: `Line 5227 of
   win32apimodule.cpp <https://github.com/mhammond/pywin32/blob/
   d3b91862b9ce9147fffba4aea9debb3a4df7cba1/win32/src/win32apimodule
   .cpp#L5227>`_

.. [DevBlogs-TONT-2010.10-18] The Old New Thing: `The evolution of the ICO file
   format, part 1: Monochrome beginnings <https://devblogs.microsoft.com/
   oldnewthing/20101018-00/?p=12513>`_

.. [DevBlogs-TONT-2010.10.22] The Old New Thing: `The evolution of the ICO file
   format, part 4: PNG images <https://devblogs.microsoft.com/oldnewthing/
   20101022-00/?p=12473>`_

.. [DevBlogs-TONT-2012] The Old New Thing: `The format of icon resources
   <https://devblogs.microsoft.com/oldnewthing/20120720-00/?p=7083>`_

.. [MSDN-ms997538] `Icons in Win32 <https://docs.microsoft.com/en-us/previous-versions/
   ms997538(v=msdn.10)?redirectedfrom=MSDN>`_

.. [MSDN-Win32-WinProg-DataTypes] Windows App Development: `Windows Data Types
   <https://docs.microsoft.com/en-us/windows/win32/winprog/windows-data-types>`_

