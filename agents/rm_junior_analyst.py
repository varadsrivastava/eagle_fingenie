from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent, UserProxyAgent
from typing import Dict, List, Union
import chromadb
from chromadb.utils import embedding_functions


class MyRetrieveUserProxyAgent(RetrieveUserProxyAgent):
    def query_vector_db(
        self,
        query_texts: List[str],
        n_results: int = 10,
        search_string: str = "",
        db_path: str = "F:/xx/xx/fingenie/data/chromadb",
        collection_name: str = "barclays_uk_products",
        **kwargs,
    ) -> Dict[str, Union[List[str], List[List[str]]]]:
        
        # define your own query function here
        client = chromadb.PersistentClient(path=db_path)
        # the collection's embedding function is always the default one, but we want to use the one we used to create the
        # collection. So we compute the embeddings ourselves and pass it to the query function.
        collection = client.get_collection(collection_name)
    
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2")

        query_embeddings = embedding_function(query_texts)
        # Query/search n most similar results. You can also .get by id
        results = collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            where_document={"$contains": search_string} if search_string else None,  # optional filter
        )
        return results

    def retrieve_docs(self, problem: str, n_results: int = 20, search_string: str = "", **kwargs):
        results = self.query_vector_db(
            query_texts=[problem],
            n_results=n_results,
            search_string=search_string,
            **kwargs,
        )

        self._results = results
        print("doc_ids: ", results["ids"])
        return self._results
