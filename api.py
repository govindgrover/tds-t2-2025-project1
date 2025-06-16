from fastapi import APIRouter

from pydantic import BaseModel
from typing import Optional

import requests
import re

from ams.settings import SETTINGS

from chromadb.api.types import QueryResult
from ams.methods.init_vectorDB import getCol
from ams.methods.accessabilty import trackAPICalls, extract_text_from_base64_image, save_question_data

# ############## [ END IMPORTS ] ##############

router = APIRouter()

class QuestionFormat(BaseModel):
	question	:	str
	image		:	Optional[str] = None	# base64-encoded image (optional)

def searchKB(query_embedding: list[float]) -> QueryResult:
	"""
	Searches the stored VectorDB

	Parameters
		`query_embeddings: list[float]` takes the embedding associated with the question asked and serach it into the 'KB' initialized

	Returns
		`QueryResult` object containing the expected results
	"""

	results = getCol().query(
		query_embeddings=[query_embedding],
		n_results=9
	)
	
	return results

def makeQEmbeds(q: str) -> list[float]:
	"""
	Make embeddings of the provided text. [context: embeddings of the asked question]

	Parameters
		`q: str` takes the string and returns its embeddings

	Returns
		`list[float]` object containing the returned embeddings for the passed string (question)
	"""

	response = requests.post(
		"https://aipipe.org/openai/v1/embeddings",
		headers={"Authorization": f"Bearer {SETTINGS.AIPIPE_API_KEY}"},
		json={"model": "text-embedding-3-small", "input": q}
	)

	data = response.json()

	info = {"total_tokens": data['usage']['total_tokens']}
	trackAPICalls(
		method		=	'makeQEmbeds'
		, resp_data	=	data
		, usage_info=	info
	)


	return data["data"][0]["embedding"]

def generateChatAnswer(student_prompt: str, source_text: list[str], image_text :str = '') -> str:
	"""
	Function to generate a complete response based on the provided context of sources and image's text

	Parameters
		`student_prompt: str` Question asked by the student
		`source_text: list[str]` Sources/references for the asked question based on the cosine similarity
		`image_text: str` extracted text from omage (optional)
		

	Returns
		`str` object or simply the answer string
	"""

	strict_prompt = """
You are a Teaching Assistant (TA) for the "Tools in Data Science" (TDS) course at IIT Madras. You are helping students by answering their course-related questions accurately and concisely.

---

You must follow these instructions strictly:

1. Use only the knowledge provided in the source text chunks below. You may use your own knowledge **only if it does not contradict the source**.
2. If the context includes module names or keywords like **LLM**, **OpenAI**, **API**, **gpt-3.5-turbo**, **gpt-4o-mini**, or similar — **use these terms exactly as given** and emphasize them using bold formatting.
3. Never ask students to clarify or rephrase their questions.
4. Do not reference past conversations or memory. Treat each question independently.
5. If a comparison is requested (e.g., between two models or methods), mention each item explicitly and compare clearly.
6. If you cannot answer using the provided context or source material, respond with:

   > "I don't have enough information to answer that question based on the available material. Please refer to the course announcements or official documents."

7. If the prompt includes "[Text extracted from image]:", treat this as valid course-related reference content. Use it along with the source context chunks to generate your answer.
8. Always maintain a tone and level similar to a TA or exam grader.
9. Do not recommend models. Instead, extract any model usage rule only from the source chunks. For example, clarify if `gpt-3.5-turbo-0125` is not supported via the proxy, but `gpt-4o-mini` is — if and only if the source explicitly states that.
10. If a question asks about using `gpt-3.5-turbo-0125` versus `gpt-4o-mini`, you must clarify that:
- `gpt-3.5-turbo-0125` is a model provided by OpenAI, and is **not usable via Anand Sir's AI Proxy**.
- The AI Proxy supports only `gpt-4o-mini` and `text-embedding-3-small`.
- Therefore, `gpt-3.5` can only be used via a direct OpenAI API key, **not** the AI Proxy.
You must not recommend a model. Instead, clearly explain the **availability constraint** based on the proxy configuration.

Example:
You are a Teaching Assistant (TA) for the TDS course at IIT Madras.
Use the following context to answer the student’s question. You may also use any additional reference marked as image text or in the text chunk or from your own.

Course Context Chunks:
{{text checnks}}

[Text extracted from image]:
{{text extracted from the image}}

Student Question:
{{prompt}}

Your Answer:
{{Your Answer}}
"""
	inps = [
		{
			'role': 'system'
			, 'content': strict_prompt
		},
		{
			'role': 'user'
			, 'content': 'Course Context Chunks:'
		},
	]
	for i in source_text:
		inps.append(
			{
				'role': 'user'
				, 'content': i
			}
		)
	
	if image_text and len(image_text.strip()) > 0:
		inps.append({
			'role': 'user'
			, 'content': '[Text extracted from image]: ' + image_text
		})

	inps.append({
		'role' :'user'
		, 'content': 'Student Question: ' + student_prompt
	})

	response = requests.post(
		"https://aipipe.org/openai/v1/responses",
		headers={"Authorization": f"Bearer {SETTINGS.AIPIPE_API_KEY}"},
		json={"model": "gpt-4o-mini", "input": inps}
	)

	data = response.json()

	info = {"total_tokens": data['usage']['total_tokens']}
	trackAPICalls(
		method		=	'generateChatAnswer'
		, resp_data	=	data
		, usage_info=	info
	)

	answer :str = data['output'][0]['content'][0]['text']


	return answer

@router.post('/api/ask/')
@router.post('/api/ask')
def ask_question(Q: QuestionFormat) -> dict:
	"""
	Parameter
	`Q: QuestionFormat` the required post data to be processed

	Returns
	`dict` (JSON) response
	"""

	image_text  = None

	# print("Q: ", Q.question)

	if Q.image:
		image_text = extract_text_from_base64_image(Q.image)

		if image_text:
			# print("I: ", Q.image[:20:] + ' ... ' + Q.image[-20::])
			image_text = re.sub(r'[^a-zA-Z0-9\s.,:;?!%-]', '', image_text)  # remove junk symbols
			image_text = re.sub(r'\s+', ' ', image_text)  # normalize spacing

			if len(image_text.split()) < 5:
				image_text = None
	# endif

	save_question_data(Q.question, Q.image)

	if image_text is not None:
		CS_result	=	searchKB(makeQEmbeds(Q.question + '\n' + image_text))
		chat_answer	=	generateChatAnswer(Q.question, [y['text'] for y in CS_result['metadatas'][0]], image_text if (len(image_text) > 0) else '')
	else:
		CS_result	=	searchKB(makeQEmbeds(Q.question))
		chat_answer	=	generateChatAnswer(Q.question, [y['text'] for y in CS_result['metadatas'][0]])

	generated_answer = chat_answer
	sources = []

	for doc in CS_result['metadatas'][0]:
		sources.append({
			"url": doc["url"],
			"text": doc["text"]
		})
	
	final_answer : dict = {
		'answer': generated_answer
		, 'links': sources
	}

	return final_answer


