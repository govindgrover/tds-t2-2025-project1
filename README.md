# TDS TA - May '25 Project

## Table of Contents

- [Introduction](#introduction)
- [Public Access](#public-access)
- [Authentication Keys](#where-the-authentication-keys-are-stored)
- [Settings](#settings)
- [Custom Logging Information](#custom-logging)

## Introduction

This project is a lightweight, developer-friendly **LLM-powered Teaching Assistant** built specifically for the **Tools in Data Science (TDS)** course at **IIT Madras** (May 2025 run). It contains tools for scraping course content and forum discussions, organizes them into a structured knowledge base (KB), and enables intelligent query handling via a backend API powered by OpenAI’s GPT models.

It also supports OCR-based image question input using [**Tesseract-OCR**](https://tesseract-ocr.github.io/), allowing students to upload screenshots or handwritten queries which are automatically parsed into text before answering.

Responses are accompanied by their original sources and reference links, making it easier for students to understand and explore each topic in depth.

Key highlights:
- 🔍 Scrapes both course and Discourse forum content.
- 🧠 Builds a local KB with optional vector embeddings.
- 🤖 Integrates with [AIPIPE](https://aipipe.org/) for LLM query routing.
- ⚙️ Offers customizable logging and clean separation of config.
- 📦 Easy to run locally — no Docker, no secrets in env vars; just drop tokens in `/.auth`.

Ideal for students, TAs, or researchers looking to build or extend intelligent assistant pipelines for academic content.

## Public Access
For Frontend: `https://tds.govindgrover.com`

For API Calling: *Find it yourself.. ;)*

## Where the Authentication Keys are stored?
This system does not use the environment variables. Rather, it read values from the `/.auth` directory, details for which are below.

> The system will **NOT RUN** if `/.auth` is *NOT PRESENT* so, kindly take care of it and use the below information at your best.

|**Filename**|**Info.**|
|---|---|
|`aipipe.token`|Paste your [AIPIPE](https://aipipe.org/) token in it|
|`auth_token.cookie`|Paste the `_t` cookie value of the [IIT Madras Discourse](https://discourse.onlinedegree.iitm.ac.in/) after loggin in there. TIP: use [inspector](https://developer.mozilla.org/en-US/docs/Learn_web_development/Howto/Tools_and_setup/What_are_browser_developer_tools)|
|`forum_session.cookie`|Paste the `_forum_session` cookie value of the [IIT Madras Discourse](https://discourse.onlinedegree.iitm.ac.in/) after loggin in there. TIP: use [inspector](https://developer.mozilla.org/en-US/docs/Learn_web_development/Howto/Tools_and_setup/What_are_browser_developer_tools)|

*If you are comfortable using the environment variables instead, simply use the [settings file]()*

## Settings

All config values are managed via a `Settings` class in `/ams/settings.py` using [`pydantic_settings`](https://docs.pydantic.dev/latest/concepts/pydantic_settings/). Values are hardcoded or loaded from token files in `/.auth`.

| Setting                     | Description                                      |
|-----------------------------|--------------------------------------------------|
| `APP_NAME`                  | Project title identifier.                        |
| `DEBUG`                     | Enable debug prints and verbose logging.         |
| `DISCOURSE_URL`             | IITM ODL Discourse forum base URL.              |
| `DISCOURSE_AUTH_TOKEN`      | Loaded from `.auth/auth_token.cookie`.          |
| `DISCOURSE_SESSION_TOKEN`   | Loaded from `.auth/forum_session.cookie`.       |
| `OUTPUT_FOLDER_C_CONTENT`   | Folder to save scraped course content.          |
| `OUTPUT_FOLDER_D_CONTENT`   | Folder to save scraped forum content.           |
| `TEMP_DISCOURSE_JSON`       | Temp file for raw Discourse data.               |
| `OUTPUT_FORMATTED_KB_DATA`  | Folder for cleaned KB output.                   |
| `AIPIPE_API_KEY`            | AI service key from `.auth/aipipe.token`.       |
| `KB_EMBEDDINGS_DATA_JSON`   | JSON file with KB embeddings.                   |
| `KB_API_LOG_PATH`           | Folder for API call logs.                       |
| `QUESTION_LOG_PATH`         | Folder to save logged student questions.        |


> Settings are instantiated as a global `SETTINGS` object and used across modules.

For first run, simply do things:
```bash
sudo apt install -y tesseract-ocr
pip install -r requirements.py
```

## Custom Logging

There are two kind of logs the system is making, one is for saving the responses from the AIPIPE's API calls while asking question. The other is of the student's question and the image in  base64 encoded format for in-future use.

The respective directories are, `/LOGS/API-CALL-LOGS` & `QA-ARCHIVE`. The same is also mentioned in the *settings* file.

Moreover, information about how much tokens costs the text is also there in the *API-CALL-LOGS*.

## References

1. ChatGPT
2. Perplexity
3. https://discourse.onlinedegree.iitm.ac.in/t/using-browser-cookies-to-access-discourse-api-in-python/173605
4.  https://github.com/sanand0/aipipe?tab=readme-ov-file#api
5. https://github.com/23f3004008/TDS-Project1-Data

---
> Built with ❤️/🧠 by [@govindgrover](https://in.linkedin.com/in/govindgrover)

*[Back to top?](#table-of-contents)*
