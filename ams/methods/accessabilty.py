import os
import json
from datetime import datetime
from typing import Dict, Any

from io import BytesIO
from PIL import Image
import pytesseract
import base64

from ams.settings import SETTINGS

# ############## [ END IMPORTS ] ##############


def trackAPICalls(method: str, resp_data: Dict[str, Any], usage_info: Dict[str, Any]) -> None:
	"""
	Logs API call metadata, usage information, and response data to a daily log file.

	This function creates a JSON Lines (`.jsonl`) file named by the current date
	in a predefined log directory (`SETTINGS.KB_API_LOG_PATH`) and appends one
	record per API call.

	Parameters:
		method (str): Name or identifier of the API method invoked.
		resp_data (Dict[str, Any]): Response data returned by the API.
		usage_info (Dict[str, Any]): Metadata about usage such as tokens, user, etc.

	Returns:
		None
	"""

	# Ensure the log directory exists
	os.makedirs(SETTINGS.KB_API_LOG_PATH, exist_ok=True)

	# Log file with today's date
	today_str = datetime.now().strftime('%Y-%m-%d')
	log_file = os.path.join(SETTINGS.KB_API_LOG_PATH, f"api_log_{today_str}.jsonl")

	# Create JSONL record
	record = {
		"timestamp": datetime.now().isoformat(),
		"method": method,
		"usage_info": usage_info,
		"response_data": resp_data
	}

	# Append to the log file
	with open(log_file, "a", encoding="utf-8") as f:
		f.write(json.dumps(record) + "\n")

def print_api_logs_if_debug(date: str = None) -> None:
	"""
	Reads and prints formatted API logs from a `.jsonl` file if debugging is enabled.

	Intended for use during development. Only works if `SETTINGS.DEBUG` is True.
	Defaults to logs from today unless a specific date is provided.

	Parameters:
		date (str, optional): Date string in 'YYYY-MM-DD' format. If None, uses today.

	Returns:
		None
	"""

	if not SETTINGS.DEBUG:
		return

	log_date = date or datetime.now().strftime('%Y-%m-%d')
	log_file = os.path.join(SETTINGS.KB_API_LOG_PATH, f"api_log_{log_date}.jsonl")

	if not os.path.exists(log_file):
		print(f"[Log Viewer] No log file found for date: {log_date}")
		return

	print(f"\n[Log Viewer] Showing logs from {log_file}:\n")

	with open(log_file, "r", encoding="utf-8") as f:
		for i, line in enumerate(f, start=1):
			try:
				record = json.loads(line)

				# Compact view for debug readability
				method = record.get("method", "Unknown")
				timestamp = record.get("timestamp", "N/A")
				usage = record.get("usage_info", {})
				response = record.get("response_data", {})
				resp_preview = str(response)[:120].replace("\n", " ").strip() + "..."

				print(f"[{i}] {timestamp} | Method: {method}")
				print(f"     Usage: {usage}")
				print(f"     Response Preview: {resp_preview}")
				print("-" * 80)

			except Exception as e:
				print(f"[Error] Failed to parse line {i}: {e}")

def extract_text_from_base64_image(base64_str: str) -> str:
	"""
	Extracts text content from a base64-encoded image using Tesseract OCR.

	The function decodes the image, ensures it's in a compatible format,
	and applies OCR to return the extracted string.

	Parameters:
		base64_str (str): The base64-encoded image content.

	Returns:
		str: The text extracted from the image. Returns an empty string if OCR fails.
	"""
	
	pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

	try:
		image_data = base64.b64decode(base64_str)
		image = Image.open(BytesIO(image_data))

		# Ensure the image is in a Tesseract-compatible format (RGB)
		if image.mode not in ("RGB", "L"):
			image = image.convert("RGB")

		text = pytesseract.image_to_string(image).strip()
		return text

	except Exception as e:
		print(f"[OCR Error] {e}")
		return ""

def save_question_data(question: str, image_base64: str = None) -> None:
	"""
	Saves a question and optional image (in base64) to a log file for record-keeping.

	Each entry is appended to a JSON Lines file with a timestamp. The output path
	is defined by `SETTINGS.QUESTION_LOG_PATH`.

	Parameters:
		question (str): The question text to log.
		image_base64 (str, optional): Optional base64 string of the associated image.

	Returns:
		None
	"""

	os.makedirs(SETTINGS.QUESTION_LOG_PATH, exist_ok=True)

	try:
		record = {
			"timestamp": datetime.utcnow().isoformat(),
			"question": question.strip()
		}

		if image_base64:
			record["image_base64"] = image_base64.strip()

		with open(os.path.join(SETTINGS.QUESTION_LOG_PATH, 'qa_data.jsonl'), "a", encoding="utf-8") as f:
			f.write(json.dumps(record) + "\n")

		if SETTINGS.DEBUG:
			print(f"--------- [QuestionLog Saved] ---------\n\n")

	except Exception as e:
		print(f"[QuestionLog Error] {e}")

