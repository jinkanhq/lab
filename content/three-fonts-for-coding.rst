三款代码字体：Fira Code、JetBrains Mono 与 Cascadia Code
########################################################
:date: 2020-03-25 22:18
:author: nt
:category: Uncategoried
:tags: 字体, 等宽字体
:slug: three-fonts-for-coding
:status: published
:feature: /images/2020/pexels-pixabay-248515-1024x512.jpg
:abstract: 这是一篇“在什么场景下使用什么字体”的小小心得，但没有做严谨的横向对比

这是一篇“在什么场景下使用什么字体”的小小心得，但没有做严谨的横向对比。

先说结论
--------

-  Fira Code

   -  字体更饱满，但也需要更大屏幕空间。
   -  笔者主要用于 IDE（字号较大，同屏文字少）。

-  JetBrains Mono

   -  风格接近 Consolas，强调阅读的流畅感，同时兼顾辨识度。
   -  笔者主要用于文本编辑器（字号较小，同屏文字多）。

-  Cascadia Code

   -  辨识度更强，大小写区分感强，符号区分感强。
   -  笔者主要用于命令行（每行文字较多，需要强调行距感）。

例子
----

♦ Fira Code

.. image:: /images/2020/fira-code.jpg

♦ JetBrains Mono

.. image:: /images/2020/jetbrains-mono.jpg

♦ Cascadia Code

.. image:: /images/2020/cascadia-code.jpg

一些信息
--------

-  Fira Code 基于 Mozilla Fira Mono 字体。
-  Cascadia Code 来自微软。
-  三款字体均支持连字（ >= <= => -> != <> 这类两字并作一符，且仍占两格），也均有非连字版本。
-  三款字体均强调了 'l' 的辨识度。

::

   反例： lll111lll1l1l1l （不同浏览器/客户端可能字体不同）

安装使用
--------

-  Fira Code

   -  `https://github.com/tonsky/FiraCode/releases <https://github.com/tonsky/FiraCode/releases>`__
   -  如果你不知道用哪个，安装 otf 目录下的所有字体即可。

-  JetBrains Mono

   -  `https://github.com/JetBrains/JetBrainsMono/releases <https://github.com/JetBrains/JetBrainsMono/releases>`__
   -  安装 ttf 目录下所有字体即可。

-  Cascadia Code

   -  `https://github.com/microsoft/cascadia-code/releases <https://github.com/microsoft/cascadia-code/releases>`__
   -  目前有四个变种，Mono 表示不连字，PL 表示 PowerLine。
   -  如果你不知道用哪个，把四个都装上。

JetBrains 系 IDE：

.. image:: /images/2020/jetbrains-font-config.jpg

VS Code：

.. code-block:: text

   // 在 settings.json 中添加该行
   // 别忘了逗号
   "editor.fontFamily": "'Jetbrains Mono', Consolas, 'Courier New', monospace"

Windows Terminal：

.. code-block:: text

   // 在 profiles.json 中，为每个需要设置字体的 profile 都添加该行
   // 别忘了逗号
   "fontFace": "Cascadia Code PL"

如果你使用 zsh，Cascadia Code PL 为你提供了 PowerLine 符号。

如果你不喜欢连字，可以换成 Cascadia Mono PL。

吐槽
----

-  笔者用了很多年 Consolas，第一眼看这些新字体看不出什么名堂，也看不出适不适合自己，于是硬着头皮“先用一阵子再说”。
-  这三款字体各自用了一个月，体会到它们确实理念更人性化、设计更有细节考量。于是现在统统用新字体了。
-  不用不知道，用于命令行的字体，和用于代码排版的字体，其侧重还是有微妙的不同。
-  个人体会，Fira Code 更倾向于代码，Cascadia Code 更倾向于命令行，JetBrains Mono 较为折衷。
-  Fira Code 在字号够大时，其饱满、清晰的优势才能体现出来，小字号还是算了。
-  （某种意义上，调大字号也是逼自己写更简洁的代码

（完）
