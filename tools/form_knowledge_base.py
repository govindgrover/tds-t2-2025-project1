from fastapi import APIRouter

import os
import json

from bs4 import BeautifulSoup
import re

from ams.settings import SETTINGS

# ############## [ END IMPORTS ] ##############

router = APIRouter()


def clean_text(raw_text: str) -> str:
	"""
	Cleans and simplifies raw Markdown or HTML-rich text for downstream processing.

	This function performs the following steps:
		- Strips YAML frontmatter (e.g., metadata between --- markers).
		- Removes image links in Markdown syntax.
		- Converts Markdown hyperlinks to plain text (retaining visible link text only).
		- Removes Markdown heading markers (e.g., `#`, `##`).
		- Cleans up table formatting artifacts and decorative dividers.
		- Replaces special characters like smart quotes and ellipses with plain equivalents.
		- Removes embedded HTML tags using BeautifulSoup.
		- Returns a single-line, stripped plain text string.

	Parameters:
		raw_text (str): The input text that may contain Markdown, HTML, or other formatting.

	Returns:
		str: Cleaned, plain text content suitable for analysis or display.
	"""

	# Strip frontmatter
	raw_text = re.sub(r"^---[\s\S]*?---\n", "", raw_text)

	# Convert markdown links/images
	raw_text = re.sub(r"!\[.*?\]\((.*?)\)", "", raw_text)  # remove image links
	raw_text = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", raw_text)  # keep visible link text only

	# Optional: remove heading hashes
	raw_text = re.sub(r"^#+\s*", "", raw_text, flags=re.MULTILINE)

	raw_text = re.sub(r"\n\s*#\s*", "", raw_text)
	raw_text = re.sub(r"\|\s*---\s*\|.*", "", raw_text)
	raw_text = re.sub("\\n[-=_]{1,}\\n", "", raw_text)
	raw_text = re.sub("\\n", "", raw_text)

	raw_text = raw_text.replace("…", "").replace("’", "'").replace("“", '"').replace("”", '"')

	# Remove any embedded HTML (if present)
	raw_text = BeautifulSoup(raw_text, "html.parser").get_text()

	return raw_text.strip()


@router.get('/form_kb')
def form_kb():
	"""
	Performs filtering oprations on the collected datasets of Discourse and Website
	and save only the needed attributes into a file named, `formatted_scraped_kb.json`
	"""

	# open discourse-scraps
	D_scrap						=	json.load(open(os.path.join(SETTINGS.OUTPUT_FOLDER_D_CONTENT, 'discourse_posts.json')))
	D_formatted	: list[dict]	=	[]

	for item in D_scrap:
		tmp = dict()

		tmp['title']	=	item['topic_title']
		tmp['tags']		=	item['tags']
		tmp['author']	=	item['author']
		tmp['url']		=	item['url']
		tmp['text']		=	clean_text(item['content'])

		D_formatted.append(tmp)

	# open C-contents-scraps
	C_scrap						=	json.load(open(os.path.join(SETTINGS.OUTPUT_FOLDER_C_CONTENT, 'metadata.json')))
	C_formatted	: list[dict]	=	[]

	tracking_appneded = []

	for item in C_scrap:
		tmp = dict()

		if item['filename'] in tracking_appneded:
			continue

		tmp['title']	=	item['title']
		tmp['tags']		=	[]
		tmp['author']	=	[]
		tmp['url']		=	item['original_url']
		tmp['text']		=	clean_text(open(os.path.join(SETTINGS.OUTPUT_FOLDER_C_CONTENT, item['filename'])).read())

		tracking_appneded.append(item['filename'])
		C_formatted.append(tmp)


	all_formatted_scraped_data = D_formatted + [{}]

	saved_filename = os.path.join(SETTINGS.OUTPUT_FORMATTED_KB_DATA, 'formatted_scraped_kb.json')
	json.dump(
		all_formatted_scraped_data
		, open(saved_filename, 'w')
		, indent=4
	)

	return {
		"status": f"Done!! check file, {saved_filename}"
	}

