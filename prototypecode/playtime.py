import newspaper
import itertools
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

""" A very hacky attempt """


def extract_newspaper(source_url):
	""" Receives url and returns a list of downloaded articles with text and keywords"""
	news_anchor = newspaper.build(source_url,memoize_articles=False)
	full_paper = []
	for article in news_anchor.articles[0:10]:
		article.download()
		try:
			article.parse()
			article.nlp()
			full_paper.append(article)
		except:
			pass
	return full_paper

def vectorize_on_dict(full_paper):
	""" receives a list of articles and vectorizes on keywords from articles"""
	articles = [' '.join(f.keywords) for f in full_paper]	
	#articles = list(itertools.chain(*articles))
	#print articles[0]
	#print articles
	vectorizer = TfidfVectorizer()
	vectorizer.fit_transform(articles)
	return vectorizer, vectorizer.fit_transform(articles)



if __name__ == '__main__':
	cnn = extract_newspaper('http://cnn.com')
	vectorizer, tfidf_matrix = vectorize_on_dict(cnn)
	print tfidf_matrix
	print vectorizer.get_feature_names()

	fox_news_article = newspaper.Article(url="http://edition.cnn.com/2014/09/25/world/meast/abu-dhabis-newest-record-solar-powered-flight/index.html")
	fox_news_article.download()
	fox_news_article.parse()
	fox_news_article.nlp()
	print fox_news_article.keywords
	fox_news_vectorized = vectorizer.transform([' '.join(fox_news_article.keywords)])

	print fox_news_vectorized
	print cosine_similarity(fox_news_vectorized, tfidf_matrix)
