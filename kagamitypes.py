from typing import TypedDict


class KagamiLink(TypedDict, total=False):
    name: str
    url: str


class KagamiTaxonomy(TypedDict, total=False):
    display_name: str
    feature: str
    description: str


class KagamiAuthor(KagamiTaxonomy):
    avatar: str


class KagamiCategory(KagamiTaxonomy):
    pass


class KagamiTag(KagamiTaxonomy):
    pass


class KagamiBadgeDefinition(TypedDict):
    label: str
    message: str
    color: str
    link: str
