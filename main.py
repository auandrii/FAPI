from fastapi import FastAPI, Security, HTTPException, Depends
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_401_UNAUTHORIZED
from celery import Celery
from pydantic import BaseModel
from crawler import crawl_and_extract_text
import asyncio
import socket
from urllib.parse import urlparse


app = FastAPI()

VALID_API_KEYS = {"ht515167fws91zts3gg5be16xy", "ht50y5j2ej58xb7mfb5j5yv4xy3333"}
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


# Define the Pydantic model for request payload
class CrawlRequest(BaseModel):
    url: str


# Initialize Celery with RabbitMQ as the broker and Redis as the backend
celery_app = Celery(
    'crawler',
    broker='amqp://user:password@rabbitmq',  # Update credentials
    backend='redis://redis:6379/0'
)


def is_api_key_valid(api_key: str = Security(api_key_header)) -> bool:
    return api_key in VALID_API_KEYS


@app.post("/crawl")
async def crawl_site(request: CrawlRequest, x_api_key: str = Depends(api_key_header)):
    """
    Endpoint to initiate site crawling.
    """
    if not is_api_key_valid(x_api_key):
        return HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    url = request.url
    if '//' not in url:
        url = '%s%s' % ('http://', url)
    if not get_dns_info(url):
        return {"Error": f"Unable to resolve domen name {urlparse(url).hostname}"}
    task = crawl_site_task.delay(url)
    return {"task_id": task.id}


@celery_app.task(bind=True)
def crawl_site_task(self, url):

    try:
        # Since Playwright is asynchronous, we need to run it inside an event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        processed_text = loop.run_until_complete(crawl_and_extract_text(url))

        # Cache the result with a 12-hour expiration
        self.backend.client.set(url, processed_text, ex=43200)

        return processed_text
    except Exception as e:
        # Implement your logging mechanism here
        print(f"Error in crawl_site_task: {str(e)}")
        return "Failed to process the URL"


@app.get("/")
async def root():
    return {"message": "OK"}


@app.get("/status/{task_id}")
async def get_task_status(task_id: str, x_api_key: str = Depends(api_key_header)):
    """
    Endpoint to check the status of a crawling task.
    """
    if not is_api_key_valid(x_api_key):
        return HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    task_result = celery_app.AsyncResult(task_id)
    if task_result.successful():
        return {"status": "completed", "text": task_result.result}
    elif task_result.failed():
        return {"status": "failed"}
    else:
        return {"status": "in progress"}


def get_dns_info(url: str) -> bool:
    d_name = urlparse(url).hostname
    try:
        socket.getaddrinfo(d_name, None, socket.AF_UNSPEC)
        return True
    except socket.gaierror as e:
        print(f"Error: Unable to resolve '{d_name}': {e}")
        return False
