Python CAPI 的简单使用
######################
:date: 2020-06-18 20:59
:author: shigure
:category: Uncategoried
:tags: API, C, Python
:slug: python-c-api-tutorial
:status: published
:feature: /images/2020/adventure-arid-daylight-847402-1024x590.jpg
:abstract: 之前开发一个模块，涉及到调用 Python 的 C API，这里是一些笔记

之前开发一个模块，涉及到调用 Python 的 C API。主要功能是：在 CPP 编写的程序中，先将数据转成 Python 对象\ ``PyObject``\ ，传入 Python 脚本，再将返回值写回程序中。其实就是间接调用 Python 脚本，有输入和输出。

* Python版本：3.6
* clang版本：3.4.2
* 本机：MacOS
* 本机头文件目录：\ ``/XX/anaconda3/include/python3.6m``\ 。

安装 Python 以后，在安装目录下的\ ``include/python3.6m``\ 中即可找到。

环境配置
========

如果想用自定义路径的 Python：\ ``export CPLUS_INCLUDE_PATH=/xxx/include/python3.7m/``

设置默认 Python 路径：

.. code:: bash

   alias python2='/YourLib/bin/python2.7'
   alias python3='/YourLib/bin/python3.6'
   alias python=python3


编译环境
--------

由于需要 Python 的库，当使用 cmake 时，需要添加：

.. code:: cmake

   set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -I${PROJECT_SOURCE_DIR}/your_path/python3.6/include/python3.6m -I /your_path/python3.6.include/python3.6m -Wno-unused-result -Wsign-compare -DNDEBUG -g -fwrapv -03 -Wall -Wstrict-prototypes")
   set(CMAKE_EXE_LINKER_FLAGS "-L /your_path/python3.6/lib -L /your_path/python3.6/lib -lpython3.6m -lpthread -ldl -lutil -lm -Xlinker -export-dynamic")
   TARGET_LINK_LIBRARIES(your_exe_file python3.6m)

Docker 镜像封装
------------------

由于需要将可执行文件放到 Docker 中，这一步骤也花费了一些时间。无此需求的盆友可以略过本小节。

.. code:: docker

   FROM busybox:1.29.3
   RUN set -ex \
     \
     && wget http://ftp.gnu.org/gnu/gcc/gcc-4.5.1/gcc-4.5.1.tar.bz2 \
     && wget https://www.python.org/ftp/python/3.6.5/Python-3.6.5.tar.xz
     && wget https://www.python.org/ftp/python/2.7.2/Python-2.7.2.tar.xz
     && tar -xvf Python-2.7.2.tar.xz
     && tar -xvf Python-3.6.5.tar.xz
     && cd Python-2.7.2.tar.xz
     && cd Python-3.6.5.tar.xz
     && ./configure prefix=/usr/local/python3  

发现无法处理中文。目前还没招到好的方法解决。

后来在 Alpine 上安装 python2 和 python3 共存的环境。

.. code:: docker

   FROM alpine:3.8
   RUN apk add --no-cache python \
     && python -m ensurepip \
     && rm -r /usr/lib/python*/ensurepip \
     && pip install --upgrade pip setuptools \
     && rm -r /root/.cache \
     && apk add --no-cache python3 \
     && rm -r /usr/lib/python*/ensurepip \
     && pip3 install --upgrade pip setuptools && \
     rm -r /root/.cache

发现无法使用 locale 指令，仍然无法解决。

最后，放弃 python2，使用 Ubuntu 和 Python3.6 环境。

.. code:: docker

   FROM python:3.6.10-buster
   RUN apt-get update \
         && apt-get install wget locales
   RUN pip3 install numpy -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com
   RUN pip3 install scipy -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com
   RUN pip3 install numpy hanziconv pandas scipy blaze nltk snownlp -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com
   # pandas scipy scikit-learn
   RUN locale-gen zh_CN.UTF-8
   RUN chmod 0755 /etc/default/locale
   ENV LC_ALL=zh_CN.UTF-8
   ENV LANG=zh_CN.UTF-8
   ENV LANGUAGE=zh_CN.UTF-8
   RUN ln -fs /bin/bash /bin/sh
   RUN  rm -rf /var/lib/apt/lists/*
   CMD ["bash"]

.. code:: docker

   FROM python3_ubuntu:v0.0.1
   ENV DEBIAN_FRONTEND = noninteractive
   RUN pip3 install numpy hanziconv pandas scipy blaze nltk snownlp -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com
   CMD ["bash"]

引用头文件
==========

最好不要用\ ``#include``\ 这种形式。

调用 Python 的 C API 时，必须引用这个头文件，由于有一些预处理的定义会影响标准库，所以所以必须优先于其他的标准头文件。

如果编译时提示\ ``no such file``\ 说明环境还有些问题。可参考 `StackOverflow <https://stackoverflow.com/questions/21530577/fatal-error-python-h-no-such-file-or-directory>`_ 或者像上文中，export目标path即可。

编译时可使用参数\ ``-framework Python``：

::
   
   gcc(或g++) sample.cpp -o sample -framework Python

常用函数
========

初始化
------

``Py_Initialize()和Py_Finalize(void);``\ 定义在\ ``pylifecycle.h``\ 中：

.. code:: cpp

   PyAPI_FUNC(void) Py_Initialize(void);
   PyAPI_FUNC(void) Py_Finalize(void);

用于初始化 Python 解释器、加载\ ``sys.modules``\ 还有些其他的功能。先调用这个函数，再调用其他 Python C API 函数。

以下三个函数也定义在\ ``pylifecycle.h``\ 中。遇到\ ``wchar_t*``\ 参数的时候，可以用\ ``Py_DecodeLocale()``\ 做编码转换。

.. code:: cpp

   PyAPI_FUNC(void) Py_SetProgramName(const wchar_t *);
   PyAPI_FUNC(void) Py_SetPythonHome(const wchar_t *);
   PyAPI_FUNC(void)      Py_SetPath(const wchar_t *);

这三个函数应先于\ ``Initialize()``\ 调用。

如果遇到：

::

   Fatal Python error: Py_Initialize: Unable to get the locale encoding

把前面的多余设置去掉就可以了。

线程相关
--------

GIL
~~~

#. | ``PyGILState_STATE PyGILState_Ensure()``
   | 确保当前线程准备好调用 C API，可以跳过当前 Python 的状态和 GIL 锁。

#. | ``void PyGILState_Release(PyGILState_STATE)``\ 函数：
   | 释放当前获取的所有资源，调用后，Python 状态将保持不变。

#. ``int PyGILState_Check()``\ 如果当前线程拥有 GIL 锁，返回 1。

.. code:: cpp

   class EnsureGilState {
   public:
       EnsureGilState() {
           _state = PyGILState_Ensure();
       }
       ~EnsureGilState() {
           PyGILState_Release(_state);
       }
   private:
       PyGILState_STATE _state;
   }

多线程
~~~~~~

#. ``PyThreadState``\ 对象，记录 Python 线程状态。

#. ``PyThreadState* PyEval_SaveThread()``\ 如果 GIL 锁已经创建，并且将线程状态变成\ ``NULL``\ ，释放 GIL 锁。

#. ``void PyEval_RestoreThread(PyThreadState *tstate)``

#. ``PyEval_InitThreads();``\ 初始化并且获取 GIL 锁。应该在主线程调用，在调用其他线程之前。

   .. code:: cpp

      class EnableThreads {
      public:
      EnableThreads() {
          _state = PyEval_SaveThread();
      }
      ~EnableThreads() {
          PyEval_RestoreThread(_state);
      }
      private:
      PyThreadState* _state;
      };

运行python脚本
----------------


``PyRun_SimpleString``\ 定义在\ ``pythonrun.h``\ 中。

.. code:: cpp

   PyAPI_FUNC(int) PyRun_SimpleStringFlags(const char *, PyCompilerFlags *);
   # define PyRun_SimpleString(s) PyRun_SimpleStringFlags(s, NULL)

比如：

.. code:: cpp

   PyRun_SimpleString("import sys");
   // or
   PyRun_SimpleString("import sys;import csv;");

模块导入
--------

``PyImport_ImportModule``\ 定义在\ ``import.h``

.. code:: C++

   PyAPI_FUNC(PyObject *) PyImport_ImportModule(
        const char *name            /* UTF-8 encoded string */
        );

例如在同目录下写一个\ ``test_add.py``\ 。

.. code:: python

   def func(a, t_str):
       if (t_str == "" or t_str == None):
           return func_1(a)
       else:
           return func_2(a, int(t_str))

   def func_1(a):
       return a+1
   def func_2(a, b):
       return a+b

   print(func(1,""))

   print(func(1,2))

然后调用。

.. code:: C++

   std::string module_name = "test_add"; // test_add.py
   PyObject* pModule = PyImport_ImportModule(module_name.c_str());

其中遇到个问题：

::

   Undefined symbols for architecture x86_64 ，后面是__basic_string blah blah


，把\ ``gcc``\ 改成\ ``g++``\ 解决。（clang同理）

**注意**\ ：只获得\ ``pModule``\ ，未必会成功。不成功的原因可能有以下几种：

#. 名字不对，比如用\ ``main``\ 这类名字；
#. 脚本内有错误：这种情况想要排查的话，使用\ ``PyErr_Print()``\ 即可。

所以，要在获取\ ``pModule``\ 之后加 Check，否则容易引起后续问题。

.. code:: C++

   if (!_pModule) {
       PyErr_Print();
       std::cout << "Fatal" << std::endl;
       exit(1);
   }

Python 的 C API 有一些关于异常的处理，后面详细讲。

获取 Python 脚本中的函数对象
-------------------------------

``PyObject_GetAttrString``

::

   PyObject* pTestFunc = PyObject_GetAttrString(pModule, "func");
   // 同上，加一个check。
   if（!PyCallable_Check(pTestFunc)) {
       PyErr_Print();
       std::cout << "Fatal" << std::endl;
       exit(1);
   }

构建输入对象
------------

在上面的脚本中，用\ ``func``\ 可能有两种执行结果：如果第二个参数是空或者\ ``None``\ ，则调用\ ``func_1``\ ，否则调用\ ``func_2``\ 。

比如，我需要把一个值，或者两个值输入到 Python 脚本的\ ``func``\ 函数中。这里的\ ``num``\ 是一个参数，按奇数偶数采取不同的含参数。

.. code:: c++

   PyObject* args = nullptr;
   PyObject* arg1 = PyInt_FromLong(100);
   if (num%2 == 0) {
       args = PyTuple_New(2);
       std::string test_str = "20";
       PyObject* arg2 = Py_BuildValue("s", test_str.c_str());
       PyTuple_SetItem(args, 0, arg1);
       PyTuple_SetItem(args, 1, arg2);
   } else {
       args = PyTuple_New(1);
       PyTuple_SetItem(args, 0, arg1);
   }

``Py_BuildValue(X, Y)``\ 这个函数，用到的\ ``X``\ 为格式字符串，代表属性的类型。一般有\ ``"s"``\ 、\ ``"i"``\ 等等。可参考\ `这里 <https://docs.python.org/release/1.5.2p2/ext/parseTuple.html>`__\ 。

构建输出对象
------------

.. code:: c++

   PyObject* pRet = PyObject_CallObject(pFunc, args);

获取结果
--------

.. code:: c++

   int iRet = 0;
   PyArg_Parse(pRet, "i", &iRet);
   std::cout << iRet << std::endl;

   Py_XDECREF(pRet);
   Py_XDECREF(args);

``Py_XDECREF``\ 用来对引用计数执行减一操作。与\ ``Py_DECREF``\ 的区别是：会对\ ``NULL``\ 进行处理。如果不执行减一操作，很可能会发生内存泄露。

错误和异常处理
--------------

* ``PyErr_Print()``\ : 如果调用之前发生错误，则会发出一些错误信息。
* ``PyErr_Clear()``\ ：清除错误信息。
 
在调试多线程时，发现\ ``PyErr_Print()``\ 不能正常调用。如果需要打印 Python 脚本的报错信息，可以用\ ``traceback``\ 记录的内容。

.. code:: C++

   void print_err() {
       PyObject* ex = PyErr_Occurred();
       PYObject *ptype, *pvalue, *ptraceback;
       PyErr_Fetch(&type, &pvalue, &ptraceback);
       if (ex) {
           PyTracebackObject* tb = (PyTracebackObject *)ptraceback;
           std::cout << "Traceback: " << std::endl;
           while (tb != nullptr) {
               PyObject *line = PyUnicode_FromFormat("File \"%U\", line %d, in %U\n",
               tb->tb_frame->f_code->co_filename, tb->tb_lineno, tb->tb_frame->f_code->co_name);
               std::cout << PyUnicode_1BYTE_DATA(line);
               tb = tb->tb_next;
           }
       PyObject* ptypeStr = PyObject_Str(ptype);
       PyObject* pvalueStr = PyObject_Str(pvalue);
       std::cout << "ERROR IS" << PyUnicode_AsUTF8(pvalueStr) << std::endl;
       std::cout << "ERROR TYPE" << PyUnicode_AsUTF8(ptypeStr) << std::endl;
       }
   } 

内存相关
--------

引用计数
~~~~~~~~

.. code:: cpp

   void Py_DECREF(PyObject *o);
   void Py_XDECREF(PyObject *o);
   void Py_CLEAR(PyObject *o)

引用计数用于内存管理，可以统计对象被引用了多少次并且给出一些处理。当引用计数为0的时候，将执行\ ``deallcoate``\ 操作（对象中的一个函数指针）。除了可以控制内存以外，还可以帮助判断一个对象是否存在。如果引用计数大于 0，那么说明对象的生存周期还没有结束。

关于引用计数的变化情况，文档中是这样介绍的：

   In theory, the object’s reference count goes up by one when the variable is made to point to it and it goes down by one when the variable goes out of scope.

Ownership of reference: 这里的“所有权”，意味着有权限执行\ ``Py_DECREF``\ 。

传递对象的引用给函数的时候有两种情形：可能“偷走”引用或者不。“偷走”引用意味着当传递引用给函数的时候，函数假设其“拥有”了引用。比如\ ``PyList_SetItem()``\ 和\ ``PyTuple_SetItem()``。

``Py_INCREF(PyObject *o)``\ ：增加引用计数

文档中关于安全性的一些建议：

   A safe approach is to always use the generic operations (functions whose name begins with PyObject\*, PyNumber\*, PySequence\* or PyMapping\*). These operations always increment the reference count of the object they return.

REF
===

| https://docs.python.org/3.6/c-api/index.html
| https://docs.python.org/3/c-api/memory.html
