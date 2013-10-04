CS257-Crawler
=============

Adam Canady  
Carleton College, Jeff Ondich, CS257  
October 4, 2013

This project is a single-threaded web crawler that returns a number of basic useful functionalities
directed towards webmasters or website content managers.

Usage: 
    <pre>./crawler.py [--linklimit int | infinity] [--searchprefix string] [--action "brokenlinks" | "outgoinglinks" | "summary"] url</pre>

Note: an option given as a searchprefix will be tested as being inside a URL string, not just a prefix. This
functionality allows the crawler to work on multiple subdomains if just a root domain is given (e.g. carleton.edu).
Additionally, all URLs will be processed without a trailing "/" to allow for greater flexibility in intra-site
navigation conventions.

This crawler pauses for 1/10th of a second between requests to avoid imposing denial of service attacks on webservers.


Some code in this project was derived from Jeff Ondich's web-precrawler.py. Additionally, the
breadth-first-search algorithm was derived from the following Stack Overflow article:
http://stackoverflow.com/questions/16755546/python-breadth-first-search-capable-of-returning-largest-distance
