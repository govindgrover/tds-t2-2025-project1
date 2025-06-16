import json
import chromadb
from chromadb.config import Settings

from ..settings import SETTINGS

from chromadb.api.models.Collection import Collection

# ############## [ END IMPORTS ] ##############


VEC_DB_COLLECTION = None

def initialize_vector_db() -> Collection:
	"""
	Function to initialize the VectorDB into memory

	Returns
		`Collection` object of the ChromaDB
	"""

	client = chromadb.Client(Settings())

	global VEC_DB_COLLECTION

	try:
		VEC_DB_COLLECTION = client.get_collection("knowledge_base")
	except Exception:
		VEC_DB_COLLECTION = client.create_collection("knowledge_base")


	if len(VEC_DB_COLLECTION.get()["ids"]) > 0:
		print("[VectorDB] ===============================> Already initialized.")
		print(f" [VectorDB] --- ROW COUNT: {VEC_DB_COLLECTION.count()}")
		return VEC_DB_COLLECTION

	f = open(SETTINGS.KB_EMBEDDINGS_DATA_JSON, 'r')
	embed_json = json.load(f)

	cnt = 0
	for obj in embed_json:
		VEC_DB_COLLECTION.add(
			ids=[f"doc_{cnt}"],
			embeddings=[obj["embeddings"]],
			metadatas=[{"title": obj["data"]['title'], 'url': obj["data"]["url"], 'text': obj["data"]["text"]}],
		)

		cnt += 1

	print("[VectorDB] ===============================> Loaded into memory.")
	print(f"[VectorDB] --- ROW COUNT: {VEC_DB_COLLECTION.count()}")

	return VEC_DB_COLLECTION

def getCol() -> Collection:
	"""
	Function to get the VectorDB vaiable for performaing further operations

	Returns
		`Collection` object of the ChromaDB
	"""
	return VEC_DB_COLLECTION
