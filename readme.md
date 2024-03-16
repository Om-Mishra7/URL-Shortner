# URL Shortener API

This API allows users to shorten long URLs into shorter, more manageable URLs. It also provides functionality to retrieve statistics for shortened URLs.

## Features

- Shorten long URLs.
- Set expiration time for shortened URLs.
- Retrieve statistics for individual URLs.
- Retrieve statistics for all shortened URLs.
- Health check to ensure the API and MongoDB connection are operational.

## Technologies Used

- FastAPI: FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints.
- MongoDB: MongoDB is a NoSQL database program, using JSON-like documents with optional schemas.
- Uvicorn: Uvicorn is a lightning-fast ASGI server.

## Installation

1. Clone the repository:

    ```bash
    git clone <repository_url>
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```


3. Set up environment variables:
   - Create a `.env` file in the root directory.
   - Add the following environment variables:
     ```
     MONGODB_URI=<your_mongodb_uri>
     AUTHORIZATION_TOKEN=<your_authorization_token>
     ```

4. Run the server:

    ```bash
    python server/app.py
    ```

## API Endpoints

- **Root Endpoint**: `/`
- **Redirect Endpoint**: `/{url_id}`
- **Shorten URL Endpoint**: `/api/v1/shorten`
- **URL Stats Endpoint (for a specific URL)**: `/api/v1/stats/{url_id}`
- **URL Stats Endpoint (for all URLs)**: `/api/v1/stats`
- **Health Check Endpoint**: `/api/v1/health`

For detailed information about each endpoint, refer to the [API documentation](https://url.om-mishra.com/docs).
