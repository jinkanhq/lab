import sys
import pelican
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple
from copy import deepcopy

BASE_DIR = Path(__file__).parent.absolute()
PLUGIN_DIR = BASE_DIR / "plugins"

sys.path.append(str(BASE_DIR))
sys.path.append(str(PLUGIN_DIR))


from kagamitypes import KagamiAuthor, KagamiCategory, KagamiBadgeDefinition, KagamiLink
from shields_io_cache import get_svg_filename


AUTHOR = "jinkan.org"
SITENAME = "人间实验室"
SITEURL = "https://lab.jinkan.org"
THEME = "themes/kagami-pelican"

PATH = "content"
TIMEZONE = "Asia/Shanghai"
DEFAULT_LANG = "zh-cn"
DEFAULT_PAGINATION = 10

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# URL prefixes
ARTICLE_URL = "{date:%Y}/{date:%m}/{date:%d}/{slug}/"
ARTICLE_SAVE_AS = "{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html"
PAGE_URL = "pages/{slug}/"
PAGE_SAVE_AS = "pages/{slug}/index.html"

# Plugins
PLUGIN_PATHS = [str(PLUGIN_DIR)]
PLUGINS = ["shields_io_cache", "webassets"]

# Kagami globals
PELICAN_VERSION: str = pelican.__version__
KAGAMI_USE_JSDELIVR: bool = False
KAGAMI_COPYRIGHT_HOLDER: str = "Jinkan"
KAGAMI_COPYRIGHT_YEAR: str = f"2013-{datetime.now().year}"
KAGAMI_SLOGAN: str = "非典型互联网技术笔记与杂谈"
KAGAMI_FAVICON: str = "images/favicon.png"

# Kagami links
KAGAMI_FOOTER_LINKS: Tuple[KagamiLink] = (
    {
        "name": "人间",
        "url": "https://jinkan.org",
    },
    {
        "name": "Github",
        "url": "https://github.com/jinkanhq"
    },
    {
        "name": "新浪微博",
        "url": "https://weibo.com/jinkanhq"
    },
    {
        "name": "知乎专栏",
        "url": "https://zhuanlan.zhihu.com/jinkan"
    },
    {
        "name": "作者团队",
        "url": "/authors.html"
    },
    {
        "name": "分类目录",
        "url": "/categories.html"
    }
)

# Kagami badges
KAGAMI_BADGES: Tuple[KagamiBadgeDefinition] = (
    {
        "label": "license",
        "message": "CC-BY-NC-SA",
        "color": "green",
        "link": "https://creativecommons.org/licenses/by-nc-sa/4.0/"
    },
    {
        "label": "pelican",
        "message": f"v{PELICAN_VERSION}",
        "color": "blue",
        "link": "https://github.com/getpelican/pelican/"
    },
    {
        "label": "theme",
        "message": "kagami-pelican",
        "color": "#6b7dd6",
        "link": "https://github.com/jinkanhq/kagami-pelican/"
    }
)

# Kagami taxonomies
KAGAMI_AUTHORS: Dict[str, KagamiAuthor] = {
    "yinian": {
        "display_name": "亦念",
        "avatar": "/images/authors/yinian.jpg",
        "description": "饱食终日，无所用心，一败涂地"
    },
    "nt": {
        "display_name": "嗯了个踢",
        "description": "（宇宙人）",
        "avatar": "/images/authors/nt.png",
    },
    "shigure": {
        "display_name": "紫吴",
        "description": "CPP，人上人",
        "avatar": "/images/authors/shigure.jpg"
    }
}
KAGAMI_CATEGORIES: Dict[str, KagamiCategory] = {
    "Uncategoried": {
        "display_name": "未分类",
        "description": "找不到分类的迷途羔羊..."
    }
}
KAGAMI_TAGS: Dict[str, KagamiCategory] = {
}
KAGAMI_TAXONOMIES: Dict[str, Dict] = {
    "author": KAGAMI_AUTHORS,
    "category": KAGAMI_CATEGORIES,
    "tag": KAGAMI_TAGS
}
