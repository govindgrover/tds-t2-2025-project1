from fastapi import APIRouter

import os
import json
import requests

from ams.settings import SETTINGS

# ############## [ END IMPORTS ] ##############

router = APIRouter()

def append_json_line(file_path: str, data: dict) -> None:
	"""
	With this function we can append each line of `data: dict` in the specified file with filepath = `file_path: str`
	"""

	with open(file_path, "a", encoding="utf-8") as f:
		json_line = json.dumps(data, ensure_ascii=False)
		f.write(json_line + ",\n")


def get_embeddings(content: str) -> list[float]:
	"""
	FUnction to create embeddings of the provided text string

	Parameter
		`content: str` the string of text for which the embedding has to be created

	Returns
		`list[float]` the embedding for the provided string
	"""

	response = requests.post(
		"https://aipipe.org/openai/v1/embeddings",
		headers={"Authorization": f"Bearer {SETTINGS.AIPIPE_API_KEY}"},
		json={"model": "text-embedding-3-small", "input": content}
	)

	data = response.json()

	info = {"total_tokens": data['usage']['total_tokens']}

	return {
		"output": data["data"][0]["embedding"]
		, "info": info
	}


@router.get('/make_embeds')
def form_kb():
	"""
	Creates embedding for each text of the filtered post data of Discourse and Website
	and save it with the data itself into a file named, `kb_with_embeddings.json`

	Also, `kb_with_embeddings.json` is our database to load into the VectorDB.
	"""

	# open formatted-scraps
	F_scrap				=	json.load(open(os.path.join(SETTINGS.OUTPUT_FORMATTED_KB_DATA, 'formatted_scraped_kb.json')))
	created_embeddings	=	[]
	counter				=	0

	for item in F_scrap:
		print("CURRENT INDEX", counter, "URL: ", item['url'])
		x = get_embeddings(item['text'])

		dcdt = {
				"embeddings": x['output']
				, "data": item
				, "api_call_info": x['info']
			}

		created_embeddings.append(dcdt)
		append_json_line('./tmp-embeddings.txt', dcdt)


		counter += 1

	saved_filename = os.path.join(SETTINGS.OUTPUT_FORMATTED_KB_DATA, 'kb_with_embeddings.json')

	json.dump(
		created_embeddings
		, open(saved_filename, 'w')
		, indent=4
	)

	return {
		"status": f"Done!! check file, {saved_filename}"
	}

