import json
import os, subprocess
from time import sleep
from datetime import datetime

from typing import Optional
from fastapi import APIRouter, Query

import requests
from bs4 import BeautifulSoup

from ams.methods import connect_discourse
from ams.settings import SETTINGS

# ############## [ END IMPORTS ] ##############

router = APIRouter()

"""
***********************************************************
********* [ FUNCS FOR SCRAPING (DISCOURSE ONLY) ] *********
***********************************************************
"""

DATE_FROM = datetime(2025, 1, 1)
DATE_TO = datetime(2025, 4, 14)


def parse_date(date_str):
	try:
		return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
	except ValueError:
		return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")


def get_paginated_topics(session: requests.Session, limit: int | None) -> list[dict]:
	"""
	Find topics for HARDCODED Category ID "34"

	Parameters
		`session: requests.Session` active session, obtained from pasting browser cookies into the specified files in the /.auth directory

	Returns
		`list[dict]` of such topics
	"""

	all_topics = []
	page_num = 0

	print("\n**************************************************")
	print("In --> get_paginated_topics()")
	print("**************************************************\n")

	if os.path.exists(f"{SETTINGS.OUTPUT_FOLDER_D_CONTENT}/__discourse_topics.json"):
		print("LOADING TOPICS FROM FILE...")
		return json.loads(open(f"{SETTINGS.OUTPUT_FOLDER_D_CONTENT}/__discourse_topics.json", 'r').read())

	while True:
		url = f"{SETTINGS.DISCOURSE_URL}/c/courses/tds-kb/34.json?page={page_num}"
		res = session.get(url)
		data = res.json()

		print("GETTING FOR: page ", page_num)

		topics = data.get("topic_list", {}).get("topics", [])

		if not topics:
			break

		all_topics.extend(topics)
		page_num += 1

		if ((limit is not None) and (page_num >= limit)):
			break

	print("\n**************************************************")
	print(f"Found {len(all_topics)} topics in category 34")
	print("**************************************************\n")
	
	json.dump(all_topics, open(f"{SETTINGS.OUTPUT_FOLDER_D_CONTENT}/__discourse_topics.json", "w", encoding="utf-8"))
	
	return all_topics

"""
This block of code will help you not calling the embedding API if previously have called
but due to some run-down it drops the chain.

What it does is that, after each good response from the API, it store the data into the `saved_posts`
with keys as the `post_id` and after a bunch of 50 (as I have specified) it stores it into the
`SETTINGS.TEMP_DISCOURSE_JSON` file.
"""
if os.path.exists(SETTINGS.TEMP_DISCOURSE_JSON):
	with open(SETTINGS.TEMP_DISCOURSE_JSON, "r", encoding="utf-8") as f:
		saved_posts = json.load(f)
else:
	saved_posts = {}

# Ensure it's a dict (keyed by post_id)
if isinstance(saved_posts, list):
	saved_posts = {str(p["post_id"]): p for p in saved_posts}


def fetch_posts_for_topic(session: requests.Session, topic_dict: dict) -> list[dict]:
	"""
	Find posts related to the topic for HARDCODED Category ID "34"

	Parameters
		`session: requests.Session` active session, obtained from pasting browser cookies into the specified files in the /.auth directory
		`topic_dict: dict` the topic details for which the posts have to be fetched

	Returns
		`list[dict]` of such posts
	"""

	topic_id = topic_dict["id"]
	topic_title = topic_dict["title"]
	topic_tags = topic_dict["tags"]

	stream_ids = session.get(f"{SETTINGS.DISCOURSE_URL}/t/{topic_id}.json").json()['post_stream']['stream']
	extracted_posts = []

	timer = 0

	for post_id in stream_ids:
		if timer > 50:
			n = 5
			with open(SETTINGS.TEMP_DISCOURSE_JSON, "w", encoding="utf-8") as f:
				json.dump(saved_posts, f, indent=2, ensure_ascii=False)
			print(f"SAVED TO {SETTINGS.TEMP_DISCOURSE_JSON} FILE")
			print(f'SLEEPING FOR {n} SECONDS')

			sleep(n)
			timer = 0

		post_url = f"{SETTINGS.DISCOURSE_URL}/t/{topic_id}/posts.json?post_ids[]={post_id}&include_suggested=false"

		if str(post_id) in saved_posts:
			print(f"Skipping Post ID {post_id} — already saved")
			continue

		try:
			print(f"Fetching Post ID: {post_id}")
			response = session.get(post_url)
			response.raise_for_status()
			post_data = response.json()

			posts = post_data.get("post_stream", {}).get("posts")
			if not posts:
				continue

			post = posts[0]
			if post["id"] != post_id:
				print(f"Warning: ID mismatch for expected {post_id}, got {post['id']}")
				continue

			# Extract text and skip if cooked is empty or whitespace
			plain_text = BeautifulSoup(post["cooked"], "html.parser").get_text().strip()
			if not plain_text:
				print(f"Skipping Post ID {post_id} - empty content")
				continue

			a_post : dict = {
				"topic_id": topic_id,
				"topic_title": topic_title,
				"tags": topic_tags,
				"post_id": post["id"],
				"post_number": post["post_number"],
				"author": post["username"],
				"created_at": post["created_at"],
				"updated_at": post["updated_at"],
				"reply_to_post_number": post.get("reply_to_post_number"),
				"reply_count": post.get("reply_count", 0),
				"url": post_url,
				"content": plain_text,
			}

			extracted_posts.append(a_post)
			saved_posts[str(post["id"])] = a_post
	
			timer += 1

		except Exception as e:
			print(f"Failed to fetch post ID {post_id}: {e}")
			continue

	return extracted_posts


"""
***********************************************************
******************* [ SCRAPING ROUTES ] *******************
***********************************************************
"""


@router.get("/scrap/discourse")
def scrap_tds_discourse(
	limit_title_pages: Optional[int] = Query(default=None, description="Optional limit on the number of Discourse title pages to scrape")
):
	"""
	Requests the IITM TDS Discourse and stores json posts.
	"""

	session = connect_discourse.create_session_with_browser_cookies(
		SETTINGS.DISCOURSE_URL,
		{
			"_t": SETTINGS.DISCOURSE_AUTH_TOKEN,
			"_forum_session": SETTINGS.DISCOURSE_SESSION_TOKEN,
		},  # Credential cookies, Extracted from browser
	)

	if not connect_discourse.verify_session_authentication(session):
		return {
			"error": "Login expired!"
		}


	all_topics = get_paginated_topics(session, limit_title_pages)
	filtered_posts = []

	print("\n**************************************************")
	print("In --> scrap_tds_discourse()")
	print("**************************************************\n")

	for topic in all_topics:
		created_at = parse_date(topic["created_at"])

		if DATE_FROM <= created_at <= DATE_TO:
			print("GETTING FOR: ", topic["slug"])

			posts = fetch_posts_for_topic(session, topic)
			filtered_posts.extend(posts)
			
			with open("./after-each-topic-saved.json", "w", encoding="utf-8") as f:
				json.dump(saved_posts, f, ensure_ascii=False)

	# os.makedirs(SETTINGS.OUTPUT_FOLDER_D_CONTENT, exist_ok=True)

	with open(f"{SETTINGS.OUTPUT_FOLDER_D_CONTENT}/discourse_posts.json", "w", encoding="utf-8") as f:
	# with open("thePOST.json", "w", encoding="utf-8") as f:
		json.dump(filtered_posts, f, indent=4, ensure_ascii=False)

	print("\n**************************************************")
	print(
		f"Scraped {len(filtered_posts)} posts of IIT-M Discourse from {DATE_FROM.date()} to {DATE_TO.date()}"
	)
	print("**************************************************\n")

	return {"message": f"IIT-M Discourse from {DATE_FROM.date()} to {DATE_TO.date()} has been scraped", "post_length": len(filtered_posts)}


@router.get("/scrap/content")
def scrap_tds_content():
	"""
	Crawls the IITM TDS course content site and stores markdown pages.
	"""

	print("\n**************************************************")
	print("In --> scrap_tds_content()")
	print("**************************************************\n")

	venv_python = os.path.join(os.getcwd(), ".env", "Scripts", "python.exe")

	result = subprocess.run(
		[venv_python, "scrape_web_contents.py", SETTINGS.OUTPUT_FOLDER_C_CONTENT],
		capture_output=True,
		text=True,
		check=True
	)

	print("WAIT THE SCRIPT IS DOING ITS WORK!!!!!")

	return {"message": f"Internal seprate python script had run, pls ckeck the folder {SETTINGS.OUTPUT_FOLDER_C_CONTENT}"}
