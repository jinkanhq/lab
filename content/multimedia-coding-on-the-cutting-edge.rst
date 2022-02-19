笔记：新锐图像、视频、音频编码格式
##################################
:date: 2020-03-25 22:11
:author: nt
:category: Uncategoried
:tags: 图像编码, 编码, 视频编码, 音频编码
:slug: multimedia-coding-on-the-cutting-edge
:status: published
:feature: /images/2020/curve-industry-photography-vintage-65128.jpg
:abstract: 笔者之前调研过一些编码格式，这些格式可能不够普及，但在某些方面有相当的优势。如果你需要在专用领域使用更高效的格式，可以参考一下这篇笔记

笔者之前调研过一些编码格式，这些格式可能不够普及，但在某些方面有相当的优势。如果你需要在专用领域使用更高效的格式，可以参考一下这篇笔记。

图像（无损）
===================

♦ FLIF

-  开源开放，立即可用。
-  压缩比上几乎是目前最优。
-  支持有损（先进行有损预处理，实际压缩存储仍为无损）。
-  缺点是编解码均较耗时。

图像（有损）
===================

♦ BPG

-  开源。
-  压缩比远胜 JPEG。
-  也支持无损压缩，但优势不明显。
-  基于 HEVC（H.265），和 HEIC / HEIF 是孪生姐妹。
-  因含 HEVC 的技术，可能有专利风险。相应的，有 HEVC 授权的设备可无限制使用 BPG。
-  举例：在游戏领域的应用，使用 BPG 存储纹理，资源下载后再在本地转换为 dds 格式供 D3D 加载，可大幅减少下载体积。

♦ HD Photo

-  微软的格式（.wdp）。
-  压缩比略逊于 BGP。

♦ webP

-  和更新锐的格式比，已然沦为“老旧格式”（非贬义）。
-  优势在于兼容性（Google系），且已经较广应用。

♦ PNG (limitpng)

-  使用 limitpng，可有损压缩。
-  也支持无损，均有效缩减体积。

♦ JPEG (Guetzli / MozJPEG)

-  JPEG 可以使用 Guetzli（Google）或 MozJPEG（Mozilla）编码器进行更高效的压缩。
-  MozJPEG 可调范围更广。
-  Guetzli 压缩比有微弱优势，但现有工具压缩速度很慢。
-  解压（解码）速度，两者均出色。

视频
===================
♦ AVS2

-  国产编码格式，对标 H.265。
-  按测试报告，在 4K 下压缩比略优于 HEVC，编码性能明显优于 HEVC。

♦ AV1

-  VP9（Google）的继任者，抗衡 HEVC。
-  免专利费。
-  尚未大规模应用，可以关注 YouTube 对此的应用进展。

音频
===================

♦ Opus

-  优秀的新格式，开源、开放。
-  分为两套方案：Opus Voice（SILK 的继任者），Opus Music（CELT 的继任者）。
-  举例：语音通话软件 Teamspeak 目前默认使用 Opus Voice。
-  值得一提的是，Opus 的推荐采样率是 48 kHz，不直接支持 44.1kHz（\ `OpusFAQ - XiphWiki <https://link.zhihu.com/?target=https%3A//wiki.xiph.org/OpusFAQ%23How_do_I_use_44.1_kHz_or_some_other_sampling_rate_not_directly_supported_by_Opus.3F>`__\ ）。

（完）
