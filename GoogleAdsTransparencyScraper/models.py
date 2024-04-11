from pydantic import BaseModel
from typing import Literal

# Search Suggestions

class SearchSuggestionsAdvertiser(BaseModel):
    name: str
    advertiser_id: str
    region: str

class SearchSuggestionsDomain(BaseModel):
    domain: str

SearchSuggestions = list[SearchSuggestionsAdvertiser | SearchSuggestionsDomain]

# Search Creatives

class SearchCreativesText(BaseModel):
    advertiser_id: str
    creative_id: str
    archive_image_url: str
    format: Literal['TEXT']
    advertiser_name: str
    advertiser_domain: str

class SearchCreativesImage(BaseModel):
    advertiser_id: str
    creative_id: str
    # click_url: str | None = None
    # image_url: str | None = None
    # title: str | None = None
    # description: str | None = None
    html: str | None = None
    archive_image_url: str | None = None
    format: Literal['IMAGE']
    advertiser_name: str
    advertiser_domain: str

class SearchCreativesVideo(BaseModel):
    advertiser_id: str
    creative_id: str
    # click_url: str | None = None
    # video_url: str | None = None
    # title: str | None = None
    # description: str | None = None
    html: str | None = None
    format: Literal['VIDEO']
    advertiser_name: str
    advertiser_domain: str

class SearchCreatives(BaseModel):
    creatives: list[SearchCreativesText | SearchCreativesImage | SearchCreativesVideo]
    cursor: str | None = None