# Legal Document Analyzer - Backend

This README provides a comprehensive guide to setting up, running, and using the backend service for the Legal Document Analyzer application. This service is responsible for processing, analyzing, and managing legal documents using advanced AI and OCR technologies.

## Table of Contents

- [About The Project](#about-the-project)
- [Key Features](#key-features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Running with Docker (Recommended)](#running-with-docker-recommended)
  - [Running Locally](#running-locally-for-development)
- [API Endpoints](#api-endpoints)
- [Docker Configuration Details](#docker-configuration-details)

## About The Project

The Legal Document Analyzer backend is a powerful FastAPI application designed to handle complex legal document processing workflows. It leverages state-of-the-art technologies like GPT-4o for OCR and text analysis to extract key information from PDF documents.

## Key Features

- **FastAPI Framework**: Modern, fast (high-performance), web framework for building APIs.
- **PDF Processing**: Extracts text and images from PDF files.
- **Advanced OCR**: Uses OpenAI's GPT-4o model to perform Optical Character Recognition on documents where text extraction is not possible.
- **Document Analysis**: Leverages `langchain` and LLMs to analyze document content and extract structured information.
 
- **Dockerized Environment**: Comes with a Docker setup for easy, consistent, and isolated deployment.

## Project Structure

Here is an overview of the key files and directories in the backend:

```
backend/
├── .env                # Stores environment variables like API keys
├── Dockerfile          # Instructions to build the Docker image
├── README.md           # This file
├── requirements.txt    # Python package dependencies
├── src/                # Main source code directory
│   ├── main.py         # FastAPI application entry point and API routes
│   ├── ingest.py       # Handles document ingestion, text extraction, and OCR
│   ├── generator.py    # Analyzes text and generates insights using an LLM
│   ├── retriever.py    # Manages document chunking and retrieval
│   ├── chunking.py     # Handles text chunking for processing
│   └── utils.py        # Utility functions
└── ...
```

## Getting Started

Follow these steps to get the backend service up and running.

### Prerequisites

Make sure you have the following software installed on your system:

- **Python 3.11+**
  ```sh
  python --version
  ```
- **Docker and Docker Compose**
  ```sh
  docker --version
  docker-compose --version
  ```

### Installation

1.  **Clone the Repository** (if you haven't already)

    ```sh
    git clone <repository-url>
    cd newclaredocs/backend
    ```

2.  **Configure Environment Variables**
    This project requires an OpenAI API key to function.

    - Create a file named `.env` in the `backend` directory.
    - Open the `.env` file and add your OpenAI API key as follows:
      ```
      OPENAI_API_KEY=sk-your-openai-api-key-here
      ```
    > **Note**: Your API key is sensitive information. The `.env` file is included in `.gitignore` to prevent it from being committed to version control.

## Usage

You can run the backend service using Docker (recommended for consistency) or locally on your machine for development.

### Running with Docker (Recommended)

The project is configured to run in a Docker container using `docker-compose`. This is the easiest and most reliable way to run the application.

1.  **Build and Start the Container**
    From the root directory of the project (`newclaredocs/`), run the following command:

    ```sh
    docker-compose up --build
    ```

    - `docker-compose up`: This command starts the services defined in `docker-compose.yml`.
    - `--build`: This flag forces Docker to rebuild the image, which is useful when you've made changes to the `Dockerfile` or application code.

2.  **Verify it's Running**
    Once the container is running, the API will be accessible at `http://localhost:8000`. You can check the API docs at `http://localhost:8000/docs`.

3.  **Stopping the Container**
    To stop the running container, press `Ctrl + C` in the terminal where `docker-compose` is running. To stop and remove the container, you can run:
    ```sh
    docker-compose down
    ```

### Running Locally (for Development)

Running the application locally is useful for development and debugging.

1.  **Navigate to the Backend Directory**

    ```sh
    cd backend
    ```

2.  **Create a Python Virtual Environment**
    It's a best practice to use a virtual environment to manage project dependencies.

    ```sh
    # Create a virtual environment named 'venv'
    python -m venv venv
    ```

3.  **Activate the Virtual Environment**

    - On **Windows**:
      ```sh
      .\venv\Scripts\activate
      ```
    - On **macOS/Linux**:
      ```sh
      source venv/bin/activate
      ```

4.  **Install Dependencies**
    Install all the required Python packages from `requirements.txt`.

    ```sh
    pip install -r requirements.txt
    ```

5.  **Run the Application**
    Use `uvicorn` to run the FastAPI application.
    ```sh
    uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
    ```
    - `src.main:app`: Tells `uvicorn` where to find the FastAPI app instance.
    - `--reload`: Automatically restarts the server when code changes are detected.

The API will be available at `http://localhost:8000`.

## API Endpoints

Here are the primary endpoints provided by the API.

### Upload a Document

- **Endpoint**: `POST /upload`
- **Description**: Uploads a PDF file for processing and analysis.
- **Example `curl` request**:
  ```sh
  curl -X POST -F "file=@/path/to/your/document.pdf" http://localhost:8000/upload
  ```

_(More endpoints can be documented here as they are developed)_

## Docker Configuration Details

The `Dockerfile` in the `backend` directory is configured to create a lightweight and efficient container for the application.

- **Base Image**: It starts from a `python:3.11-slim` image.
- **System Dependencies**: It installs `poppler-utils`, which is required for PDF processing tasks (`pdf2image` library depends on it).
- **Application Code**: It copies the application source code into the container.
- **No Python Packages**: As per your request, the `Dockerfile` **does not** install Python packages from `requirements.txt`. This assumes that dependencies are managed separately. If you need the dependencies installed in your Docker image, you should add the `pip install` steps back into the `Dockerfile`.
- **Command**: It uses `uvicorn` to run the FastAPI application, making it accessible on port 8000.
- **Environment Variables**: The container expects environment variables (like `OPENAI_API_KEY`) to be provided at runtime, typically via a `.env` file or Docker Compose configuration.
- **Port Exposure**: The container exposes port `8000` for API access.
- **Working Directory**: The working directory inside the container is set to `/app`.
- **Entry Point**: The default command runs the FastAPI application using `uvicorn`.
- **Volume Mounting**: When using Docker Compose, the source code is mounted as a volume to allow live code changes without rebuilding the image.
- **Health Checks**: You can add health check configurations in Docker Compose to monitor the application's status.
- **Logging**: Logs from the application can be viewed in the Docker container logs, useful for debugging and monitoring.
- **Scalability**: The Docker setup can be easily scaled using orchestration tools like Kubernetes or Docker Swarm if needed in the future.
- **Security**: Ensure that sensitive information like API keys are managed securely and not hardcoded into the Docker image.
For more details on the Docker configuration, refer to the `Dockerfile` and `docker-compose.yml` files in the project.
---
This README provides all the necessary information to get started with the Legal Document Analyzer backend. For further assistance or contributions, please refer to the project's contribution guidelines or contact the maintainers.
