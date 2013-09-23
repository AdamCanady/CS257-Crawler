CS257-Crawler
=============

crawler.py
Adam Canady
Jeff Ondich, CS257
September 23, 2013

This project is a single-threaded web crawler that returns a number of basic useful functionalities
directed towards webmasters or website content managers.

Usage: 
    python crawler.py [--linklimit int | infinity] [--searchprefix string] [--action brokenlinks | outgoing links | summary] url

Some code in this project was derived from Jeff Ondich's web-precrawler.py. Additionally, the
breadth-first-search algorithm was derived from the following Stack Overflow article:
http://stackoverflow.com/questions/16755546/python-breadth-first-search-capable-of-returning-largest-distance
