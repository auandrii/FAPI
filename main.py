from fastapi import FastAPI, HTTPException
from celery import Celery
from pydantic import BaseModel
from crawler import crawl_and_extract_text
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


# Define the Pydantic model for request payload
class CrawlRequest(BaseModel):
    url: str

# Initialize Celery with RabbitMQ as the broker and Redis as the backend
celery_app = Celery(
    'crawler',
    broker='amqp://user:password@rabbitmq',  # Update credentials
    backend='redis://redis:6379/0'
)

@app.post("/crawl")
async def crawl_site(request: CrawlRequest):
    """
    Endpoint to initiate site crawling.
    """
    print(request.url)
    task = crawl_site_task.delay(request.url)
    return {"task_id": task.id}

@celery_app.task(bind=True)
def crawl_site_task(self, url):
    try:
        # Since Playwright is asynchronous, we need to run it inside an event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        processed_text = loop.run_until_complete(crawl_and_extract_text(url))

        # Cache the result with a 12-hour expiration
        #self.backend.client.set(url, processed_text, ex=43200)

        return processed_text
    except Exception as e:
        # Implement your logging mechanism here
        print(f"Error in crawl_site_task: {str(e)}")
        return "Failed to process the URL"

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """
    Endpoint to check the status of a crawling task.
    """
    task_result = celery_app.AsyncResult(task_id)
    if task_result.successful():
        return {"status": "completed", "text": task_result.result}
    elif task_result.failed():
        return {"status": "failed"}
    else:
        return {"status": "in progress"}
