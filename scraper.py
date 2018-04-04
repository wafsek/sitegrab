__author__ = "Baljit Sarai"
__version__ = "1.0.1"
__maintainer__ = "Baljit Sarai"
__email__ = "saraibaljit@gmail.com"

from urllib.request import urlopen
from bs4 import BeautifulSoup, SoupStrainer
import os, sys
import warnings
import requests
import string, random
warnings.filterwarnings("ignore")


"""Change these variables to your liking"""
site_url = "http://example.com/"
site_dir = "site/"
html_dir = site_dir+"html/"
img_dir = site_dir+"img/"

site_map = {}
site_links = []
scanned_links = []
failed_pages = []
failed_media = []


def write_html(filename, data):
    f = open(filename, 'wb')
    f.write(data)
    f.close()


def find_site_links():
    """Finds all the local links on the website."""
    print("Links to be scanned  |  Unique links found")
    while site_links:
        sys.stdout.write("\r        %d           |           %d           " % (len(site_links), len(scanned_links)))
        sys.stdout.flush()
        link_url = site_links.pop(0)
        page_links = find_local_links(site_url, link_url)
        for page_link in page_links:
            if page_link.startswith("/"):
                if not is_already_scanned(site_url+page_link[1:]):
                    handle_url(page_link)
                    scanned_links.append(site_url+page_link[1:])
    print("\nDone scanning!")


def handle_url(link_url):
    site_links.append(site_url+link_url[1:])
    full_page_path = html_dir+link_url[1:]
    site_map[site_url + link_url[1:]] = full_page_path


def is_already_scanned(link):
    return link in scanned_links


def find_local_links(site_url, url):
    """Finds and returns all links on a given url"""
    links = []
    html = urlopen(url)
    site_data = html.read()
    for link in BeautifulSoup(site_data, parse_only=SoupStrainer('a')):
        if link.has_attr('href'):
            full_link = link['href']
            full_link.replace(site_url, '/')
            if not full_link.endswith("/"):
                full_link = full_link+"/"
            links.append(full_link)
    return links


def build_site_structure():
    print("Building site structure...")
    for url, path in site_map.items():
        if not os.path.exists(path):
            os.makedirs(path)
    print("Site structure built")


def copy_site_html():
    print("Unique pages found: " + str(len(site_map)))
    html = urlopen(site_url)
    filename = html_dir + "index.html"
    f = open(filename, 'wb')
    page = html.read()
    new_page = steal_all_media(page)
    f.write(new_page)
    f.close()
    counter = 1
    for url, path in site_map.items():
        try:
            html = urlopen(url)
            filename = path + "index.html"
            f = open(filename, 'wb')
            page = html.read()
            new_page = steal_all_media(page,path=path)
            f.write(new_page)
            f.close()
        except Exception as e:
            failed_pages.append(url)

        sys.stdout.write("\rPages copied %d" % counter)
        sys.stdout.flush()
        counter = counter + 1


def steal_all_media(page, path=img_dir):
    result = ""
    try:
        img_path = path.replace(html_dir, img_dir)
        if not os.path.exists(img_path):
            os.makedirs(img_path)
        soup = BeautifulSoup(page, 'html.parser')
        for img in soup.findAll('img'):
            url = img['src']
            filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            fullname = img_path + filename+url[-4:]
            img['src'] = fullname
            with open(fullname, 'wb') as f:
                if 'http' not in url:
                    # sometimes an image source can be relative
                    # if it is provide the base url which also happens
                    # to be the site variable atm.
                    url = '{}{}'.format(site_url, url)
                response = requests.get(url)
                f.write(response.content)
        my_html_string = str(soup)
        result =  bytes(my_html_string,encoding='utf8')
    except Exception as e:
        failed_media.append(page)
    return result


def report_errors():
    f = open("links_failed", 'w')
    for link in failed_pages:
        f.write(link)
    f.close()
    f2 = open("links_media", 'w')
    for link in failed_pages:
        f2.write(link)
    f2.close()


if __name__ == "__main__":
    site_links.append(site_url)
    find_site_links()
    build_site_structure()
    copy_site_html()
    report_errors()

