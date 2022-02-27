用reStructuredText编写技术图书
##############################
:date: 2018-10-25 22:47
:author: yinian
:category: Uncategoried
:tags: pandoc, reStructuredText, Sphinx
:slug: writing-book-in-restructuredtext
:status: published
:feature: /images/2018/ballpoint-pen-classic-coffee-composition-261510.jpg
:abstract: 因为翻译过一些 Flask 相关的文档，写了不少 reStructuredText 格式的文本，对 Sphinx 这个文档生成工具也是爱不释手。所以在翻译技术图书时，也就想继续运用这套工具链

前言
----

因为翻译过一些 Flask 相关的文档，写了不少 reStructuredText 格式的文本，对 Sphinx 这个文档生成工具也是爱不释手。所以在翻译技术图书时，也就想继续运用这套工具链。不过还是遇到了一些问题，尤其是在转换成\ ``.docx``\ 格式的 Word 文档时候。这里稍微做一下笔记。

reStructuredText
----------------

`reSturcturedText <http://docutils.sourceforge.net/rst.html>`_ 最早可以追溯到 Zope 开发的 StructuredText，并基于 StucturedText 改进而来。reSturcturedText 的缩写是 reST，意为 revised, reworked, and reinterpreted StructuredText。

它与 Markdown 类似，都是所见即所得的纯文本标记语法，功能比 Markdown 更强大，但也稍微复杂了一些。

对于 Python 界，它已经是文档标记语法的事实标准，Python 本身和许多第三方库的文档都是用 reStructuredText 编写的。早在2002年的 `PEP-287 <https://www.python.org/dev/peps/pep-0287/>`_ 中，就已经建议 reSturcturedText 作为 Python 中 docstring 的标记语法。

Sphinx
------

`Sphinx <http://www.sphinx-doc.org/en/master/index.html>`_\ 是一个由\ `pocoo <https://www.pocoo.org/>`_\ 团队发起的、用 Python 编写的文档生成工具，经过多年演进，现在已经可以生成 Python、C、C++、JavaScript 等多种语言的文档。在 Python 中，reStructuredText 的解析由 docutils 库完成，Sphinx 也正是基于 docutils 构建的。

编写图书其实用不到 Sphinx 的高级功能（文档测试、交叉引用等）。笔者虽然对 Sphinx 有先入为主的好感，但这里其实只是用 Sphinx 生成一份漂亮的 HTML 电子书，用于寻求友人帮助审阅。而且，在 Sphinx 生成 HTML 时，Sphinx 也会提示 reStructuredText 中的语法错误。

下面开始安装 Sphinx，然后用 Sphinx 自带的脚本工具\ ``sphinx-quickstart``\ ，根据提示配置基本的目录结构和构建脚本。下面是个人建议的起始配置。

.. code-block:: bash

   $ pip install sphinx
   $ mkdir mybook && cd mybook
   $ sphinx-quickstart
   Welcome to the Sphinx 1.8.1 quickstart utility.

   Please enter values for the following settings (just press Enter to
   accept a default value, if one is given in brackets).

   Selected root path: .

   You have two options for placing the build directory for Sphinx output.
   Either, you use a directory "_build" within the root path, or you separate
   "source" and "build" directories within the root path.
   > Separate source and build directories (y/n) [n]:    

   Inside the root directory, two more directories will be created; "_templates"
   for custom HTML templates and "_static" for custom stylesheets and other static
   files. You can enter another prefix (such as ".") to replace the underscore.
   > Name prefix for templates and static dir [_]:  

   The project name will occur in several places in the built documentation.
   > Project name: My Book
   > Author name(s): Marisa
   > Project release []:  

   If the documents are to be written in a language other than English,
   you can select a language here by its language code. Sphinx will then
   translate text that it generates into that language.

   For a list of supported codes, see
   http://sphinx-doc.org/config.html#confval-language.
   > Project language [en]: zh_CN

   The file name suffix for source files. Commonly, this is either ".txt"
   or ".rst".  Only files with this suffix are considered documents.
   > Source file suffix [.rst]:  

   One document is special in that it is considered the top node of the
   "contents tree", that is, it is the root of the hierarchical structure
   of the documents. Normally, this is "index", but if your "index"
   document is a custom template, you can also set this to another filename.
   > Name of your master document (without suffix) [index]:  
   Indicate which of the following Sphinx extensions should be enabled:
   > autodoc: automatically insert docstrings from modules (y/n) [n]: n
   > doctest: automatically test code snippets in doctest blocks (y/n) [n]: n
   > intersphinx: link between Sphinx documentation of different projects (y/n) [n]: n
   > todo: write "todo" entries that can be shown or hidden on build (y/n) [n]: y   
   > coverage: checks for documentation coverage (y/n) [n]: n
   > imgmath: include math, rendered as PNG or SVG images (y/n) [n]: y
   > mathjax: include math, rendered in the browser by MathJax (y/n) [n]: n
   > ifconfig: conditional inclusion of content based on config values (y/n) [n]: n
   > viewcode: include links to the source code of documented Python objects (y/n) [n]: n
   > githubpages: create .nojekyll file to publish the document on GitHub pages (y/n) [n]: n

   A Makefile and a Windows command file can be generated for you so that you
   only have to run e.g. `make html' instead of invoking sphinx-build
   directly.
   > Create Makefile? (y/n) [y]:  
   > Create Windows command file? (y/n) [y]:  

   Creating file ./conf.py.
   Creating file ./index.rst.
   Creating file ./Makefile.
   Creating file ./make.bat.

   Finished: An initial directory structure has been created.

   You should now populate your master file ./index.rst and create other documentation
   source files. Use the Makefile to build the docs, like so:
      make builder
   where "builder" is one of the supported builders, e.g. html, latex or linkcheck.

这里启用了 todo 扩展，让 Sphinx 支持\ ``..todo::``\ 指令的解析，可以用来标记待办或未完事宜。

这里还启用了 imgmath 扩展，Sphinx 会调用系统环境下的 latex 把数学公式渲染成图片插入到构建好的文档中，这里有一些额外的依赖。笔者是在 WSL 中的 Ubuntu 中操作的，依赖安装方法如下。

.. code-block:: bash

   $ sudo apt-get install pdfimages poppler-utils tex-live texstudio texlive texlive-latex-extra dvipng

现在初始化工作就完成了，目录结构应该是这样。

.. code-block:: bash

   mybook
   ├── _build
   ├── conf.py
   ├── index.rst
   ├── make.bat
   ├── Makefile
   ├── _static
   └── _templates

pandoc
------

pandoc 是一个 Haskell 编写的万能文档转换工具，可以在 Markdown、reStructuredText、textile、HTML、DocBook、LaTeX、Word 等多种格式中互相转换。这里用 pandoc 把 reStructuredText 转换成\ ``.docx``\ 格式的 Word 文档。基本的用法是这样，把\ ``chpater1.rst``\ 转换成\ ``chapter1.docx``\ 。

.. code-block:: bash

   $ pandoc -o chapter1.docx -f rst+east_asian_line_breaks -s chapter1.rst

默认情况下，pandoc 会把换行转换成空格，但这是为西方语言设置的默认值。对于中文，就需要开启\ ``east_asian_line_breaks``\ 选项，去除换行引入的空格。

文件结构
--------

Sphinx默认会以\ ``index.rst``\ 为入口，依次遍历读取文档，构建文档树，形成最终文档。但pandoc只是转换工具，没有构建文档树的能力，虽然可以批量转换多个文件，但其实转换每次只处理单个文件。为兼顾二者特性，笔者这里做了一个折衷。创建一个\ ``contents.inc``\ 文件，在其中填写\ `TOC <http://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-toctree>`_\ 。TOC中的各项是各章\ ``.rst``\ 的文件名。然后在\ ``index.rst``\ 中包含它。

**toc.rst**

.. code-block:: rst

   .. toctree::
      :maxdepth: 3

      chapter1
      chapter2
      chapter3

**index.rst**

.. code-block:: rst

   .. Mybook documentation master file, created by
      sphinx-quickstart on Thu Oct 19 22:17:03 2018.
      You can adapt this file completely to your liking, but it should at least
      contain the root `toctree` directive.

   Mybook
   =====================================

   Table of contents
   ---------------------

   .. include:: contents.inc

接下来读取\ ``contents.inc``\ 中的各章，并调用 pandoc。笔者是用一个简单的 Python 文件完成这一工作的，并直接保存在\ ``mybook``\ 目录下，命名为\ ``build_docx.py``\ 。

.. code-block:: python

   import os
   import pathlib

   build_path = '_build/docx'

   pathlib.Path(build_path).mkdir(parents=True, exist_ok=True)

   idx_file = open('contents.inc', 'r')
   within_toc_block = False
   build_files = []
   command = 'pandoc -o {0} -f rst+east_asian_line_breaks -s {1}'

   for line in idx_file:
       if within_toc_block == False:
           if line.startswith('.. toctree::'):
               within_toc_block = True
       else:
           if line.startswith('   :'):
               continue
           elif not line.strip(' '):
               continue
           elif line.startswith('  ') and line.strip():
               build_files.append(line.strip())

   file_args = []

   for i, f in enumerate(build_files):
       file_args.append(f + '.rst')
       output_file = os.path.join(build_path, '{0}-{1}.docx'.format(i, f))
       os.system(command.format(output_file, f + '.rst'))
       print('{0} converted successfully'.format(f))

   os.system(command.format(
       os.path.join(build_path, 'all-in-one.docx'), ' '.join(file_args)))
   print('all-in-one converted successfully')

然后再为 Makefile 添加 docx 入口，就可以用\ ``make docx``\ 命令直接生成 Word 文档了。

.. code-block:: makefile

   docx: Makefile
       @python build_docx.py

标记语法
--------

这里的 `.rst` 并非标准 reSturcturedText，而是 Sphinx 扩展的方言版本，一些常用的语法如下所示。

.. code-block:: rst

   标题与章节
   #################
   Book Title
   #################

   *******************
   Chapter 1
   *******************

   1.2 Section
   =====================

   1.2.3 Subsection
   ^^^^^^^^^^^^^^^^^^^^^^

   1.2.3.4 Paragraph
   """"""""""""""""""""""

   粗体
   **Bold**

   斜体
   *Italic*

   内联代码
   ``inline code``

   链接
   ``Chamber of Kagami <http:://kagami.jinkan.org>``_
   ``Chamber of Kagami``_

   .. _Chamber of Kagami: https://domain.invalid/

   脚注

   Lorem ipsum dolor sit amet, consectetur adipiscing elit.
   Pellentesque dignissim libero quis ipsum sagittis, vel dapibus justo dignissim [1]_.
   Quisque scelerisque dictum sapien sit amet blandit.
   Maecenas scelerisque feugiat urna in egestas. 

   .. [1] this is a footnote

   代码块
   .. code-block:: python

       import antigravity

   提示
   .. tip::

       lorem ipsum

   注解
   .. note::

       lorem ipsum

另外，中文和内联语法如果没有空格之类的字符隔开，则会出现语法错误。如果直接用空格，那么最终文档中也会有额外的空格。根据\ `reST文档规范 <http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#character-level-inline-markup>`_\ ，可以用反斜线转义空格，具体处理如下。

.. code-block:: rst

   天地有\ **大美** \而不言，四时有明法而不议，万物\ [1]_\ 有成理而不说。圣人者，原天地之美而
   达万物之理。是故至人无为，大圣不作，观于天地之谓也。

   .. [1] 这是一个脚注

更多语法可以参看 Sphinx 的\ `语法介绍部分 <http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`_\ 或者 docutils 团队维护的\ `reST语法介绍 <http://docutils.sourceforge.net/rst.html>`_\ 。
