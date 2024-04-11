import requests
import json
from bs4 import BeautifulSoup
import re
import codecs

from models import (
    # SearchSuggestions,
    SearchSuggestions,
    SearchSuggestionsAdvertiser,
    SearchSuggestionsDomain,
    
    # SearchCreatives,
    SearchCreatives,
    SearchCreativesText,
    SearchCreativesImage,
    SearchCreativesVideo,
)

CHROME_HEADERS = {
    'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'accept-language': 'en-US,en;q=0.9,pt;q=0.8',
}

class GoogleAdsTransparencyScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(CHROME_HEADERS)

    def search_suggestions(self, query: str):
        """Get Search Suggestions

        Args:
            query (str): search query

        Returns:
            SearchSuggestions: search suggestions
        """
        params = {
            'authuser': '0',
        }
        data = {
            'f.req': json.dumps({
                '1': query,
                '2': 10,
                '3': 10
            }),
        }
        response = self.session.post('https://adstransparency.google.com/anji/_/rpc/SearchService/SearchSuggestions', params=params, data=data)
        response.raise_for_status()
        result = response.json()
        results: SearchSuggestions = []
        for search_suggestion in result['1']:
            if search_suggestion_advertiser := search_suggestion.get('1'):
                results.append(SearchSuggestionsAdvertiser(
                    name=search_suggestion_advertiser['1'],
                    advertiser_id=search_suggestion_advertiser['2'],
                    region=search_suggestion_advertiser['3'],
                ))
            if search_suggestion_domain := search_suggestion.get('2'):
                results.append(SearchSuggestionsDomain(
                    domain=search_suggestion_domain['1'],
                ))
        return results

    def _parse_content_js(self, content_js: str):
        matched = re.search(r'previewservice\.insertPreviewHtmlContent\(\'(.*?)\', \'(.*?)\', \'(.*)\', (\d+), (\d+), null, (true|false), (\d+), (true|false), (\d+), (true|false), (true|false), (true|false), (true|false)\);', content_js)
        if not matched:
            return None
        arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9, arg10, arg11, arg12, arg13 = matched.groups()
        # soup = BeautifulSoup(arg3.encode().decode('unicode-escape'), 'html.parser')
        return arg3.encode().decode('unicode-escape')

    def search_creatives_by_domain(self, domain: str, cursor: str | None = None):
        params = {
            'authuser': '0',
        }
        if cursor:
            data = {
                'f.req': json.dumps({
                    '2': 40,
                    '3': {
                        '8': [2392],
                        '12': {
                            '1': domain,
                            '2': True
                        }
                    },
                    '4': cursor,
                    '7': {
                        '1': 1,
                        '2': 18,
                        '3': 2392
                    }
                }),
            }
        else:
            data = {
                'f.req': json.dumps({
                    '2': 40,
                    '3': {
                        '8': [2392],
                        '12': {
                            '1': domain,
                            '2': True
                        }
                    },
                    '7': {
                        '1': 1,
                        '2': 18,
                        '3': 2392
                    }
                }),
            }
        response = self.session.post('https://adstransparency.google.com/anji/_/rpc/SearchService/SearchCreatives', params=params, data=data)
        response.raise_for_status()
        result = response.json()
        results = SearchCreatives(creatives=[])
        results.cursor = result.get('2')
        for search_creative in result['1']:
            match search_creative['4']:
                case 1:
                    results.creatives.append(SearchCreativesText(
                        advertiser_id=search_creative['1'],
                        creative_id=search_creative['2'],
                        archive_image_url=BeautifulSoup(search_creative['3']['3']['2'], 'html.parser').find('img')['src'],
                        format="TEXT",
                        advertiser_name=search_creative['12'],
                        advertiser_domain=search_creative['14'],
                    ))
                case 2:
                    try:
                        archive_image_url = BeautifulSoup(search_creative['3']['3']['2'], 'html.parser').find('img')['src']
                    except:
                        archive_image_url = None
                    if archive_image_url:
                        results.creatives.append(SearchCreativesImage(
                            advertiser_id=search_creative['1'],
                            creative_id=search_creative['2'],
                            archive_image_url=archive_image_url,
                            format="IMAGE",
                            advertiser_name=search_creative['12'],
                            advertiser_domain=search_creative['14'],
                        ))
                    else:
                        html = self._parse_content_js(requests.get(search_creative['3']['1']['4']).text)
                        results.creatives.append(SearchCreativesImage(
                            advertiser_id=search_creative['1'],
                            creative_id=search_creative['2'],
                            html=html,
                            format="IMAGE",
                            advertiser_name=search_creative['12'],
                            advertiser_domain=search_creative['14'],
                        ))
                case 3:
                    html = self._parse_content_js(requests.get(search_creative['3']['1']['4']).text)
                    results.creatives.append(SearchCreativesImage(
                        advertiser_id=search_creative['1'],
                        creative_id=search_creative['2'],
                        html=html,
                        format="IMAGE",
                        advertiser_name=search_creative['12'],
                        advertiser_domain=search_creative['14'],
                    ))
        return results

if __name__ == '__main__':
    google_ads_transparency_scraper = GoogleAdsTransparencyScraper()
    # print(google_ads_transparency_scraper.search_suggestions('temu').domains)
    print(google_ads_transparency_scraper.search_creatives_by_domain('temu.com'))
    # google_ads_transparency_scraper._parse_content_js(requests.get('https://displayads-formats.googleusercontent.com/ads/preview/content.js?client=ads-integrity-transparency&obfuscatedCustomerId=9400287112&creativeId=670757879201&uiFeatures=12,54&adGroupId=151327612783&itemIds=4842605165526610089&overlay=%3DH4sIAAAAAAAAALMSMxLhEuJcWbB-2d5kE2dBHuNFW51Neoq8ZLgEkouLXTKLC3ISK4NLijLz0oU4uNjc8_PTc1K9VLgkijPyCwqAoo4p_mlpqUXORamJJZllqQZCHFZsHN-ZhBgZAcGfrvpcAAAA&sig=ACiVB_yMBgizmkqvLVbL9G2n3iUmrX4fSA&htmlParentId=fletch-render-4246689711494543967&responseCallback=fletchCallback4246689711494543967').text)