#!/usr/bin/env python
'''
    crawler.py
    Adam Canady
    Jeff Ondich, CS257
    September 23, 2013

    This project is a single-threaded web crawler that returns a number of basic useful functionalities
    directed towards webmasters or website content managers.

    Usage: python crawler.py [--linklimit int] [--searchprefix string] [--action brokenlinks | outgoing links | summary] url

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

# Derived from Jeff's Code
def get_links(text):
    href_pattern = re.compile(r'<a .*?href="(.*?)"')
    links = []
    for href_value in re.findall(href_pattern, text):
        links.append(href_value)
    return links

# Derived from Jeff's Code
def get_page(url):
    # Get the text of the requested page.
    try:
        response = urllib2.urlopen(url, timeout=5)
        page_contents = response.read()
        code = response.code
        response.close()
        return page_contents, code
    except Exception, e:
        return '', 404

def print_broken_links(broken_links, links_reverse):
    print "Broken Links:"
    for link in broken_links:
        for backlink in links_reverse[link]:
            print backlink + ", " + link

def print_outgoing_links(links_reverse, search_prefix):
    print "Outgoing Links:"
    for link in links_reverse:
        if search_prefix not in link:
            print link

def print_summary(startingURL, links_reverse, crawled_nodes, broken_links):
    # Process Graph (derived from Stack Overflow post linked above)
    q = Queue.Queue()
    q.put((startingURL,))
    visited = set()
    visited.add(startingURL)

    longest_path_len = 0
    longest_path = (startingURL,)
    while not q.empty():
        path = q.get()
        last_node = path[-1]
        for node in links_reverse[last_node]:
            if node not in visited:
                new_path = path + (node,)
                if len(new_path) > longest_path_len:
                    longest_path = new_path
                    longest_path_len = len(longest_path)
                q.put(new_path)
                visited.add(node)

    # FilesFound
    print "FilesFound:", len(crawled_nodes)

    # LongestPathDepth
    print "LongestPathDepth:", longest_path_len

    # LongestPath
    print "LongestPath:"
    for node in longest_path:
        print node

    # CantGetHome
    print "CantGetHome:"
    # print "Visited:", visited
    for link in crawled_nodes - visited - broken_links:
        print link

def main(arguments):
    ## Taking care of arguments ##
    if not arguments.linklimit: linklimit = 1000
    elif "infinity" in arguments.linklimit: linklimit = float('inf')
    else: linklimit = int(arguments.linklimit[0])
    startingURL = urllib2.urlopen(arguments.startingURL).geturl() # Reconcile initial redirects
    print "Initial URL Reconciled:", startingURL

    search_prefix = urlparse.urlparse(startingURL).netloc if not arguments.searchprefix else arguments.searchprefix

    ## Defining Data Structures ##
    to_crawl = Queue.Queue()
    to_crawl.put(startingURL)
    queued = set()
    queued.add(startingURL)

    # Graph components
    links_forward = {} # links_forward[link_from] = [link_to]
    links_reverse = {} # links_reverse[link_to] = [link_from]
    crawled_nodes = set()

    broken_links = set() # "url_from, url_to"

    # Make connected_to_home set
    connected_to_home = {}

    # Main loop
    while not to_crawl.empty() and len(crawled_nodes) < linklimit:
        cur_url = to_crawl.get()
        cur_page, cur_response_code = get_page(cur_url)
        crawled_nodes.add(cur_url)

        if cur_response_code == 404:
            broken_links.add(cur_url)
            # continue

        cur_page_links = get_links(cur_page)

        for link in cur_page_links:
            full_url = urlparse.urljoin(cur_url, link) # Deal with relational links

            if search_prefix in full_url and full_url not in queued:
                to_crawl.put(full_url)
                queued.add(full_url)

            # Links Forward
            if cur_url in links_forward: links_forward[cur_url].append(full_url)
            else: links_forward[cur_url] = [full_url]

            # Links Reverse
            if full_url in links_reverse: links_reverse[full_url].append(cur_url)
            else: links_reverse[full_url] = [cur_url]

        time.sleep(0.1)

    # Process the crawl
    if arguments.action and "brokenlinks" in arguments.action:
        print_broken_links(broken_links, links_reverse)

    if arguments.action and "outgoinglinks" in arguments.action:
        print_outgoing_links(links_reverse, search_prefix)


    if arguments.action and "summary" in arguments.action:
        print_summary(startingURL, links_reverse, crawled_nodes, broken_links)

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Produce a report on the web page specified on the command line.')
    arg_parser.add_argument('startingURL', help='URL to start the crawler at.')
    arg_parser.add_argument('--linklimit', action='append')
    arg_parser.add_argument('--searchprefix', action='append')
    arg_parser.add_argument('--action', action='append')
    arguments = arg_parser.parse_args()

    main(arguments)