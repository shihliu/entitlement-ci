import urllib

def get_html_source(url):
    """Accept a url and return html source"""
    sock = urllib.urlopen(url)
    htmlSource = sock.read()
    sock.close()
    # logger.debug(htmlSource)
    return htmlSource
