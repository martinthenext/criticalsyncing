"""

If the article is from Western media and mentions some other country, find a source for that country
	and search for the similar article on that source
Otherwize, look at the source of the article and find an opposite source, 
	and search for the similar article on that source
	
"""
def get_matching_url(input_url):
	return u"http://ya.ru"