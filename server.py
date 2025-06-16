"""
Author: Govind Grover
Email: reach@govindgrover.com
Date: 2025-06-16
Description: GPT-based (aipipe.org) Teaching Assistant (TA) LLM application for `Tools in Data Science` course at Indian Institute of Technology Madras.
"""

from fastapi import FastAPI

from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from ams.settings import SETTINGS
from ams.methods.init_vectorDB import initialize_vector_db

import api

# ############## [ END IMPORTS ] ##############

"""
This segment is necesarry to handle the initializtion of our VectorDB when the service starts
"""
@asynccontextmanager
async def lifespan(app: FastAPI):
	# Only initialize once, avoid reloading or subprocess issues
	import multiprocessing

	if multiprocessing.current_process().name == "MainProcess":
		initialize_vector_db()
	yield

# FastAPI Application Initializtion
app = FastAPI(title=SETTINGS.APP_NAME, debug=SETTINGS.DEBUG, lifespan=lifespan)

# Enable CORS for local development if frontend is served separately
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Adjust for production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


"""
Main route to handle the API Requests for the TDS-TA LLM
"""
app.include_router(api.router)


"""
Un-comment this section if want to:
- scrape either Discourse or Course Content Website; `scrapping`
- scrape transform the scraped data into some filtered JSON; `knowledge_base`
- scrape create embeddings of the Knowledge-Base(KB); `make_embeds`
"""
# from tools import scrapping, form_knowledge_base, make_embeds
# app.include_router(scrapping.router)
# app.include_router(form_knowledge_base.router)
# app.include_router(make_embeds.router)

"""
For server a HTML page - just for my fun.. I added this functionality :)
"""
app.mount("/", StaticFiles(directory="static", html=True), name="static")


"""
Un-comment this section if want to serve on local-machine using the command: `python server.py` 
"""
import uvicorn
if __name__ == '__main__':
	uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
