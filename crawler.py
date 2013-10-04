#!/usr/bin/env python
'''
    crawler.py
    Adam Canady
    Jeff Ondich, CS257
    October 4, 2013

    This project is a single-threaded web crawler that returns a number of basic useful functionalities
    directed towards webmasters or website content managers.

    Usage: python crawler.py [--linklimit int] [--searchprefix string] [--action brokenlinks | outgoing links | summary] url

    Note: an option given as a searchprefix will be tested as being inside a URL string, not just a prefix. This
    functionality allows the crawler to work on multiple subdomains if just a root domain is given (e.g. carleton.edu).
    Additionally, all URLs will be processed without a trailing "/" to allow for greater flexibility in intra-site
    navigation conventions.

    This crawler pauses for 1/10th of a second between requests to avoid imposing denial of service attacks on webservers.

    Some code in this project was derived from Jeff Ondich's web-precrawler.py. Additionally, the
    breadth-first-search algorithm was derived from the following Stack Overflow article:
    http://stackoverflow.com/questions/16755546/python-breadth-first-search-capable-of-returning-largest-distance
'''

import argparse
import re
import urllib2
import urlparse
import Queue
import sets
import time

class Crawl():

    def __init__(self, arguments):
        self.arguments = arguments
        self.process_arguments(self.arguments.linklimit, self.arguments.startingURL, self.arguments.searchprefix)

        self.main()

    def process_arguments(self, link_limit, startingURL, search_prefix):
        ## Take care of arguments ##
        if not link_limit: self.link_limit = 1000
        elif "infinity" in link_limit: self.link_limit = float('inf')
        else: self.link_limit = int(link_limit[0])

        self.startingURL = urllib2.urlopen(startingURL).geturl() # Reconcile initial redirects
        self.search_prefix = self.startingURL if not search_prefix else search_prefix

        self.urls_to_crawl = Queue.Queue()
        self.urls_to_crawl.put(self.startingURL)
        self.queued_for_crawling = set()
        self.queued_for_crawling.add(self.startingURL)
        self.links_reverse = {} # links_reverse[link_to] = [link_from]
        self.crawled_nodes = set()
        self.crawled_path = {} # crawled_nodes[url] = (path_to_url)
        self.broken_links = set() # "url_from, url_to"

    def print_broken_links(self):
        print "Broken Links:"
        for link in self.broken_links:
            for backlink in self.links_reverse[link]:
                print backlink + ", " + link

    def print_outgoing_links(self):
        print "Outgoing Links:"
        for link in self.links_reverse:
            if self.search_prefix not in link:
                print link

    def print_summary(self):
        # Process Graph (derived from Stack Overflow post linked above)
        q = Queue.Queue()
        q.put((self.startingURL,))
        visited = set()
        visited.add(self.startingURL)

        while not q.empty():
            path = q.get()
            last_node = path[-1]
            for node in self.links_reverse.get(last_node,[]):
                if node not in visited:
                    new_path = path + (node,)
                    q.put(new_path)
                    visited.add(node)

        # Find longest path
        longest_path_len = 0
        longest_path = ()
        for key in self.crawled_path:
            path = self.crawled_path[key]
            if len(path) > longest_path_len:
                longest_path = path
                longest_path_len = len(path)

        # FilesFound
        print "FilesFound:", len(self.crawled_nodes)

        # LongestPathDepth
        print "LongestPathDepth:", longest_path_len

        # LongestPath
        print "LongestPath:"
        for node in longest_path:
            print node

        # CantGetHome
        print "CantGetHome:"

        for link in self.crawled_nodes - visited - self.broken_links:
            print link

    def do_crawl(self):
        while not self.urls_to_crawl.empty() and len(self.crawled_nodes) < self.link_limit:
            cur_url = self.urls_to_crawl.get()
            cur_page = Page(cur_url)

            self.crawled_nodes.add(cur_url)

            if cur_page.response_code == 404:
                self.broken_links.add(cur_url)

            for link in cur_page.links:
                full_url = urlparse.urljoin(cur_url, link) # Deal with relational links

                if self.search_prefix in full_url and full_url not in self.queued_for_crawling:
                    self.urls_to_crawl.put(full_url)
                    self.queued_for_crawling.add(full_url)

                    # Generate Path
                    if self.crawled_path.get(cur_url):
                        self.crawled_path[full_url] = self.crawled_path.get(cur_url) + (full_url,)
                    else:
                        self.crawled_path[full_url] = (self.startingURL, full_url)

                # Links Reverse
                if full_url in self.links_reverse: self.links_reverse[full_url].append(cur_url)
                else: self.links_reverse[full_url] = [cur_url]

            time.sleep(0.1)

    def process_crawl(self):
        # Process the crawl
        if self.arguments.action and "brokenlinks" in self.arguments.action:
            self.print_broken_links()

        if self.arguments.action and "outgoinglinks" in self.arguments.action:
            self.print_outgoing_links()

        if self.arguments.action and "summary" in self.arguments.action:
            self.print_summary()

    def main(self):
        self.do_crawl()
        self.process_crawl()

class Page():
    def __init__(self, url):
        self.url = url
        self.get_page()
        self.get_links()

    # Derived from Jeff's Code
    def get_links(self):
        href_pattern = re.compile(r'<a .*?href="(.*?)"')
        links = []
        for href_value in re.findall(href_pattern, self.content):
            links.append(href_value)
        self.links = links

    # Derived from Jeff's Code
    def get_page(self):
        # Get the text of the requested page.
        try:
            response = urllib2.urlopen(self.url, timeout=5)
            self.content = response.read()
            self.response_code = response.code
            response.close()
        except Exception, e:
            self.content = ''
            self.response_code = 404

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Produce a report on the web page specified on the command line.')
    arg_parser.add_argument('startingURL', help='URL to start the crawler at.')
    arg_parser.add_argument('--linklimit', action='append')
    arg_parser.add_argument('--searchprefix', action='append')
    arg_parser.add_argument('--action', action='append')
    arguments = arg_parser.parse_args()

    Crawl(arguments)
