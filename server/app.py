import os
import uuid
import time
import dotenv
import secrets
import uvicorn
from pymongo import MongoClient
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse

dotenv.load_dotenv()

# MongoDB connection
mongodb_client = MongoClient(os.getenv("MONGODB_URI"))
db = mongodb_client["url-shortener"]
urls_collection = db["urls"]

# FastAPI app
app = FastAPI(app_name="URL Shortener API | ProjectRexa", version="0.1.0", summary="This API allows users to shorten long URLs into shorter, more manageable URLs. It also provides functionality to retrieve statistics for shortened URLs.", title="URL Shortener API | ProjectRexa", description="This API allows users to shorten long URLs into shorter, more manageable URLs. It also provides functionality to retrieve statistics for shortened URLs.", docs_url="/docs", redoc_url=None, openapi_url="/openapi.json",  contact={
        "name": "Om Mishra",
        "url": "https://om-mishra.com",
        "email": "om@om-mishra.com"
    })


# Middleware to add process time header
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    try:
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        return JSONResponse(content={
            "status": "error",
            "message": f"An error occurred: {str(e)}",
            "request_id": str(uuid.uuid4())
        })

# Root endpoint
@app.get("/")
async def root():
    return JSONResponse(content={
        "status": "success",
        "message": "URL Shortener API",
        "request_id": str(uuid.uuid4())
    })

# Redirect short URLs
@app.get("/{url_id}")
async def redirect(url_id: str):
    try:
        if len(url_id) != 7:
            return JSONResponse(content={
                "status": "error",
                "message": "Invalid URL ID",
                "request_id": str(uuid.uuid4())
            })
        
        original_url = urls_collection.find_one({"url_id": url_id.lower()})

        if not original_url:
            return JSONResponse(content={
                "status": "error",
                "message": "URL ID not found, or URL expired",
                "request_id": str(uuid.uuid4())
            })
        
        if original_url["expires_at"] > 0 and (int(time.time()) - original_url["created_at"]) > original_url["expires_at"]:
            return JSONResponse(content={
                "status": "error",
                "message": "URL ID not found, or URL expired",
                "request_id": str(uuid.uuid4())
            })
        
        urls_collection.update_one({"url_id": url_id}, {"$inc": {"number_of_redirects": 1}})

        # Add headers to the response
        response = RedirectResponse(url=original_url["url"])
        response.headers["X-Original-URL"] = original_url["url"]
        response.headers["X-Redirect-URL"] = f"https://url.om-mishra.com/{url_id.lower()}"
        response.headers["Cache-Control"] = f"max-age={int(original_url['expires_at']) if original_url['expires_at'] > 0 else 0}, public"
        return response
    
    except Exception as e:
        return JSONResponse(content={
            "status": "error",
            "message": f"An error occurred: {str(e)}",
            "request_id": str(uuid.uuid4())
        })

# Shorten URLs
@app.get("/api/v1/shorten")
async def shorten(url: str, seconds_to_expire: int = 0, authorization_token: str = None, request: Request = None):
    try:
        if not url:
            return JSONResponse(content={
                "status": "error",
                "message": "Missing required parameters: URL (This is the URL you want to shorten)",
                "request_id": str(uuid.uuid4())
            })

        if seconds_to_expire < 0:
            return JSONResponse(content={
                "status": "error",
                "message": "Invalid value for the parameter: seconds_to_expire, it should be a positive integer",
                "request_id": str(uuid.uuid4())
            })
        
        if authorization_token != os.getenv("AUTHOURIZATION_TOKEN"):
            return JSONResponse(content={
                "status": "error",
                "message": "Invalid authorization token, request has been rejected",
                "request_id": str(uuid.uuid4())
            })

        url_id = secrets.token_urlsafe(5)

        while urls_collection.find_one({"url_id": url_id}):
            url_id = secrets.token_urlsafe(5)

        urls_collection.insert_one({
            "url_id": url_id.lower(),
            "url": url.strip(),
            "expires_at": seconds_to_expire,
            "created_at": int(time.time()),
            "number_of_redirects": 0,
            "created_by_user_metadata": {
                "ip": request.client.host,
                "user_agent": request.headers.get("user-agent")
            }
        })

        shortened_url = f"https://url.om-mishra.com/{url_id.lower()}"
        return JSONResponse(content={
            "status": "success",
            "message": "URL shortened",
            "shortened_url": shortened_url,
            "original_url": url,
            "expires_at": seconds_to_expire,
            "request_id": str(uuid.uuid4())
        })
    except Exception as e:
        return JSONResponse(content={
            "status": "error",
            "message": f"An error occurred: {str(e)}",
            "request_id": str(uuid.uuid4())
        })

# Get stats for a specific URL
@app.get("/api/v1/stats/{url_id}")
async def stats(url_id: str, authorization_token: str = None):
    try:
        if authorization_token != os.getenv("AUTHOURIZATION_TOKEN"):
            return HTTPException(detail="Invalid authorization token")
        
        if len(url_id) != 7:
            return HTTPException(detail="Invalid URL ID")

        original_url = urls_collection.find_one({"url_id": url_id})

        if not original_url:
            return HTTPException(detail="URL ID not found")
        
        return JSONResponse(content={
            "status": "success",
            "message": "URL stats",
            "url_id": url_id,
            "number_of_redirects": original_url["number_of_redirects"],
            "created_at": original_url["created_at"],
            "expires_at": original_url["expires_at"],
            "request_id": str(uuid.uuid4())
        })
    except Exception as e:
        return JSONResponse(content={
            "status": "error",
            "message": f"An error occurred: {str(e)}",
            "request_id": str(uuid.uuid4())
        })

# Get stats for all URLs
@app.get("/api/v1/stats")
async def stats(authorization_token: str = None):
    try:
        if authorization_token != os.getenv("AUTHOURIZATION_TOKEN"):
            return JSONResponse(content={
                "status": "error",
                "message": "Invalid authorization token, request has been rejected",
                "request_id": str(uuid.uuid4())
            })

        urls = urls_collection.find({}, {"_id": 0, "url_id": 1, "number_of_redirects": 1, "created_at": 1, "expires_at": 1})
        return JSONResponse(content={
            "status": "success",
            "message": "URL stats",
            "urls": list(urls),
            "request_id": str(uuid.uuid4())
        })
    except Exception as e:
        return JSONResponse(content={
            "status": "error",
            "message": f"An error occurred: {str(e)}",
            "request_id": str(uuid.uuid4())
        })

# Health Check
@app.get("/api/v1/health")
async def health():
    try:
        mongodb_client.server_info()
        return JSONResponse(content={
            "status": "success",
            "message": "MongoDB connection OK | Server OK | URL Shortener API",
            "request_id": str(uuid.uuid4())
        })
    except Exception as e:
        return JSONResponse(content={
            "status": "error",
            "message": f"An error occurred: {str(e)}",
            "request_id": str(uuid.uuid4())
        })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
