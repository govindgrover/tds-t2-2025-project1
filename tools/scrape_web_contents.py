"""
This whole script has to be called seprated not within the FastAPI routes since,
it is using async methods of async_playwright's chromium and I have not implemented
the asyncs there in the main application.
"""

import asyncio
import sys, os, re, json
from datetime import datetime
from markdownify import markdownify as md
from playwright.async_api import async_playwright

BASE_URL = "https://tds.s-anand.net/#/2025-01/"
BASE_ORIGIN = "https://tds.s-anand.net"
OUTPUT_DIR =  sys.argv[1]
METADATA_FILE = os.path.join(sys.argv[1], "metadata.json")

visited = set()
metadata = []

def sanitize_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "_", title).strip().replace(" ", "_")

async def extract_all_internal_links(page):
    return list(set([
        link for link in await page.eval_on_selector_all("a[href]", "els => els.map(el => el.href)")
        if BASE_ORIGIN in link and '/#/' in link
    ]))

async def wait_for_article_and_get_html(page):
    await page.wait_for_selector("article.markdown-section#main", timeout=10000)
    return await page.inner_html("article.markdown-section#main")

async def crawl_page(page, url):
    if url in visited:
        return
    visited.add(url)
    print(f"📄 Visiting: {url}")
    try:
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(1000)
        html = await wait_for_article_and_get_html(page)
    except Exception as e:
        print(f"Error loading {url}\n{e}")
        return

    title = (await page.title()).split(" - ")[0].strip() or f"page_{len(visited)}"
    filename = sanitize_filename(title)
    filepath = os.path.join(OUTPUT_DIR, f"{filename}.md")

    markdown = md(html)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"---\n")
        f.write(f'title: "{title}"\n')
        f.write(f'original_url: "{url}"\n')
        f.write(f'downloaded_at: "{datetime.now().isoformat()}"\n')
        f.write(f"---\n\n")
        f.write(markdown)

    metadata.append({
        "title": title,
        "filename": f"{filename}.md",
        "original_url": url,
        "downloaded_at": datetime.now().isoformat()
    })

    links = await extract_all_internal_links(page)
    for link in links:
        await crawl_page(page, link)

async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    global visited, metadata
    visited.clear()
    metadata.clear()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await crawl_page(page, BASE_URL)

        with open(METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        print("\n**************************************************")
        print(f"Saved {len(metadata)} course pages")
        print("**************************************************\n")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
