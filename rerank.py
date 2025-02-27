import cohere

class Reranker:
    def __init__(self, model='rerank-multilingual-v3.0'):
        self.client = cohere.Client('PruDWg2hOzOEURHnUkPnu4IfsVTa6w6n0XBYK8K9')
        self.model = model

    def rerank(self, query, documents, top_n=None):
            response = self.client.rerank(
                query=query,
                documents=documents,
                model=self.model, 
                top_n=top_n)

            reranked_results = [doc.index for doc in response.results]


            return reranked_results
