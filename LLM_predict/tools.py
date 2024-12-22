import requests

class PubMedTool:
    def __init__(self, base_url  = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'):
        self.base_url = base_url
        
    def search(self, query, max_results = 5):
        search_url = f'{self.base_url}esearch.fcgi'
        params = {
            'db': 'pubmed', 
            'term': query,
            'retmode': 'json', 
            'retmax': max_results
        }
        response = requests.get(search_url, params = params)
        response.raise_for_status()
        data = response.json()
        
        return data.get('esearchresult', {}).get('idlist', [])
    
    def fetch_article_details(self, article_id):
        fetch_url = f'{self.base_url}efetch.fcgi'
        params = {
            'db': 'pubmed', 
            'id': article_id, 
            'retmode': 'xml'
        }
        response = requests.get(fetch_url, params = params)
        response.raise_for_status()
        
        return response.text
    
    def get_articles(self, query, max_results = 5):
        article_ids = self.search(query, max_results)
        articles = []
        for article_id in article_ids:
            article_details = self.fetch_article_details(article_id)
            articles.append(article_details)
            
        return articles