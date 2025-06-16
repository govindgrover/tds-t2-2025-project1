from pydantic_settings import BaseSettings

class Settings(BaseSettings):
	"""
	Application configuration using Pydantic BaseSettings.

	This class loads environment-style configuration values, such as tokens,
	file paths, flags, and API endpoints. It is automatically instantiated at
	the bottom of the module as `SETTINGS`.

	Attributes:
		APP_NAME (str): Project name/identifier.
		DEBUG (bool): Toggle for debug behavior (prints, log viewing, etc.).

		DISCOURSE_URL (str): URL of the Discourse forum (IITM ODL).
		DISCOURSE_AUTH_TOKEN (str): Authentication token for Discourse access.
		DISCOURSE_SESSION_TOKEN (str): Session cookie for forum scraping.

		OUTPUT_FOLDER_C_CONTENT (str): Path for storing scraped course content.
		OUTPUT_FOLDER_D_CONTENT (str): Path for storing scraped forum content.
		TEMP_DISCOURSE_JSON (str): Temporary JSON file for intermediate Discourse data.

		OUTPUT_FORMATTED_KB_DATA (str): Directory to save the cleaned/structured KB output.

		AIPIPE_API_KEY (str): API key for communicating with the AI pipeline.

		KB_EMBEDDINGS_DATA_JSON (str): File path for knowledge base with vector embeddings.

		KB_API_LOG_PATH (str): Directory for storing daily API call logs.
		QUESTION_LOG_PATH (str): Directory for saving incoming question records.
	"""


	APP_NAME				:	str		=	'TDS TA - May \'25 Project'
	DEBUG					:	bool	=	True

	DISCOURSE_URL			:	str		=	'https://discourse.onlinedegree.iitm.ac.in'
	DISCOURSE_AUTH_TOKEN	:	str		=	open('./.auth/auth_token.cookie').read()
	DISCOURSE_SESSION_TOKEN	:	str		=	open('./.auth/forum_session.cookie').read()

	OUTPUT_FOLDER_C_CONTENT	:	str		=	'./scraping-output/course_content'
	OUTPUT_FOLDER_D_CONTENT	:	str		=	'./scraping-output/discourse_content'
	TEMP_DISCOURSE_JSON		:	str		=	'./inner-loop.json'

	OUTPUT_FORMATTED_KB_DATA:	str		=	'./scraping-output'

	AIPIPE_API_KEY			:	str		=	open('./.auth/aipipe.token').read()

	KB_EMBEDDINGS_DATA_JSON	:	str		=	'./scraping-output/kb_with_embeddings.json'

	KB_API_LOG_PATH			:	str		=	'./LOGS/API-CALL-LOGS'
	QUESTION_LOG_PATH		:	str		=	'./LOGS/QA-ARCHIVE'

SETTINGS = Settings()
