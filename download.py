import urllib.request
from utils.cache import cache
import parsel
from datetime import datetime
import json
import sys
import os


@cache()
def get_html(url):
    with urllib.request.urlopen(urllib.request.Request(
        url= url, 
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.62'
        }, 
        method="GET"
    )) as f:
        return f.read().decode()

def parse_page(url):
	html = get_html(url)
	sel = parsel.Selector(html)
	l = list()
	for item in sel.xpath('//*[@id="repo-content-pjax-container"]/div[2]/div[2]/div'):
		tag = item.xpath('div/div/div[1]/h4/a/text()').get().strip()
		dt = item.xpath('div/div/ul/li[1]/relative-time/@datetime').get().strip()
		l_item = dict(tag=tag, datetime=datetime.fromisoformat(dt.strip('Z')).isoformat(sep=' ', timespec='auto'))
		print(l_item)
		l.append(l_item)
	a_next = sel.xpath('//*[@id="repo-content-pjax-container"]/div[3]/div/a')[-1]
	url_new_page = a_next.xpath('@href').get()
	if a_next.xpath('text()').get() != 'Next':
		return None, list()
	return url_new_page, l

def main():
	domain = 'https://github.com'
	repo = sys.argv[1]
	path = f'/{repo}/tags'
	versions = list()
	if not os.path.exists(os.path.dirname(sys.argv[2])):
		os.makedirs(os.path.dirname(sys.argv[2]))
	while path:
		path, l = parse_page(domain+path)
		versions.extend(l)
	with open(sys.argv[2], 'w') as fp:
		json.dump(dict(total=len(versions), data=versions), fp, indent=2, ensure_ascii=False)


if __name__ == '__main__':
	main()
