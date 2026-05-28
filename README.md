# AWS S3 Explorer - MCP Server

An open-source Model Context Protocol (MCP) server built in Python that securely connects AI assistants to Amazon S3. 

This server provides Large Language Models (LLMs) with the ability to list buckets, inspect dataset structures, and read file schemas directly without requiring massive data downloads. It is engineered for ML infrastructure pipelines, featuring fully asynchronous I/O and defensive error handling.

## Features

* **Asynchronous I/O:** Utilizes `aiobotocore` for non-blocking concurrent requests, ensuring the server doesn't fall over under heavy LLM workloads.
* **Defensive Error Handling:** Catch-and-return patterns for AWS exceptions (including missing credentials) that allow AI agents to cleanly self-correct.
* **Strict Typing:** Heavily typed Python interfaces using the `FastMCP` wrapper to automatically generate robust JSON schemas for the client.
* **Mocked CI/CD:** Fully automated test suites using `pytest` and `pytest-asyncio`, integrated into a GitHub Action pipeline.

## Tools Exposed to the LLM

This server exposes three specific primitives:

1. `list_s3_buckets()`: Lists all S3 buckets accessible by the current AWS credentials.
2. `list_s3_objects(bucket_name, prefix, max_keys)`: Lists objects inside a specific bucket. Limits results by default to prevent LLM context window overflow.
3. `read_s3_file_head(bucket_name, object_key, byte_limit)`: Reads the first few kilobytes of an S3 object to inspect its contents (e.g., CSV headers, JSON structures) without downloading the entire file.

## Installation and Setup

### Prerequisites
* Python 3.11+
* AWS credentials configured locally (e.g., `aws configure` or `~/.aws/credentials`)

### Option 1: Quick Setup
If you have `uv` installed, you can quickly run the server without manual installation:
```bash
uvx aws-s3-explorer-mcp
```

### Option 2: User Setup
Install the package from PyPI:
```bash
pip install aws-s3-explorer-mcp
```
You can start the MCP server by running:
```bash
aws-s3-explorer-mcp
```

### Option 3: Developer Setup
Clone the repository and install the required dependencies:

```bash
git clone https://github.com/kbates97/AWS_S3_Explorer_MCP.git
cd AWS_S3_Explorer_MCP
python -m venv venv

# Windows: .\venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

pip install -r requirements.txt
```
You can run the server locally with:
```bash
python ./src/aws_s3_mcp/server.py
```