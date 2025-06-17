# create a new test collection without persistent client    
from chromadb.utils import embedding_functions
import chromadb
import chromadb

chroma_client = chromadb.PersistentClient(path="F:/WORK/PROJECTS/fingenie/data/chromadb")

# # switch `create_collection` to `get_or_create_collection` to avoid creating a new collection every time
# collection = chroma_client.get_or_create_collection(name="my_collection")

# # switch `add` to `upsert` to avoid adding the same documents every time
# collection.upsert(
#     documents=[
#         "This is a document about pineapple",
#         "This is a document about oranges"
#     ],
#     ids=["id1", "id2"]
# )

# results = collection.query(
#     query_texts=["This is a query document about florida"], # Chroma will embed this for you
#     n_results=2 # how many results to return
# )

# print(results)

# get_collection = chroma_client.get_collection("barclays_products", 
#                 embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2"))

# print(get_collection)

# results = get_collection.query(
#     query_texts=["This is a query document about florida"], # Chroma will embed this for you
#     n_results=2 # how many results to return
# )



# retrieve_docs = get_collection.retrieve_docs(
#     queries=["This is a query document about florida"],
#     n_results=2,
#     search_string="",
#     )


    # the collection's embedding function is always the default one, but we want to use the one we used to create the
    # collection. So we compute the embeddings ourselves and pass it to the query function.
collection = chroma_client.get_collection("barclays_products")

embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2")

query_texts=["This is a query document about florida"]

query_embeddings = embedding_function(query_texts)
    # Query/search n most similar results. You can also .get by id
results = collection.query(
        query_embeddings=query_embeddings,
        n_results=2,
        # where_document={"$contains": search_string} if search_string else None,  # optional filter
    )
  
print(results)

