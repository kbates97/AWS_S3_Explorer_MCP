import aiobotocore.session
from botocore.exceptions import ClientError, NoCredentialsError, BotoCoreError
from mcp.server.fastmcp import FastMCP

# Initialize the MCP Server
mcp = FastMCP("AWS_S3_Explorer")

# Initialize the aiobotocore session
session = aiobotocore.session.get_session()

@mcp.tool()
async def list_s3_buckets() -> list[str]:
    """
    List all Amazon S3 buckets accessible by the current AWS credentials.
    Use this to find where datasets or infrastructure logs might be stored.
    """
    try:
        async with session.create_client('s3') as client:
            response = await client.list_buckets()
            return [bucket['Name'] for bucket in response['Buckets']]
    except NoCredentialsError:
        return ["Error: AWS credentials not found. Please run `aws configure` or set your environment variables."]
    except ClientError as e:
        return [f"AWS API Error: {e.response['Error']['Message']}"]
    except BotoCoreError as e:
        return [f"AWS Connection Error: {str(e)}"]
    except Exception as e:
        return [f"Unexpected Error: {str(e)}"]

@mcp.tool()
async def list_s3_objects(bucket_name: str, prefix: str = "", max_keys: int = 50) -> list[dict]:
    """
    List objects inside a specific Amazon S3 bucket.
    
    Args:
        bucket_name: The exact name of the S3 bucket.
        prefix: Optional folder path or prefix to filter by (e.g., 'datasets/train/').
        max_keys: Maximum number of files to return (default 50) to prevent context overflow.
    """
    try:
        async with session.create_client('s3') as client:
            response = await client.list_objects_v2(
            Bucket=bucket_name, 
            Prefix=prefix, 
            MaxKeys=max_keys
        )
        
        if 'Contents' not in response:
            return [{"message": "Bucket or prefix is empty."}]
            
        return [
            {
                "key": obj['Key'],
                "size_bytes": obj['Size'],
                "last_modified": str(obj['LastModified'])
            }
            for obj in response['Contents']
        ]
    except ClientError as e:
        return [f"AWS API Error: {e.response['Error']['Message']}"]
    except NoCredentialsError:
        return ["Error: AWS credentials not found. Please run `aws configure` or set your environment variables."]
    except BotoCoreError as e:
        return [f"AWS Connection Error: {str(e)}"]
    except Exception as e:
        return [f"Unexpected Error: {str(e)}"]

@mcp.tool()
async def read_s3_file_head(bucket_name: str, object_key: str, byte_limit: int = 2000) -> str:
    """
    Read the first few kilobytes of an S3 object to inspect its contents or schema.
    Ideal for previewing CSV headers, JSON structures, or log file formats without 
    downloading massive ML datasets.
    
    Args:
        bucket_name: The name of the S3 bucket.
        object_key: The exact path/key of the file.
        byte_limit: Number of bytes to read (default 2000).
    """
    try:
        # We only fetch a specific byte range to ensure we don't crash the LLM's context window
        async with session.create_client('s3') as client:
            response = await client.get_object(
                Bucket=bucket_name, 
                Key=object_key,
                Range=f'bytes=0-{byte_limit}'
            )
            body = await response['Body'].read()
            return body.decode('utf-8', errors='replace')
    except ClientError as e:
        return f"AWS API Error: {e.response['Error']['Message']}"
    except NoCredentialsError:
        return "Error: AWS credentials not found. Please run `aws configure` or set your environment variables."
    except BotoCoreError as e:
        return f"AWS Connection Error: {str(e)}"
    except Exception as e:
        return f"Unexpected Error: {str(e)}"

def main():
    """Entry point for the package."""
    mcp.run()

if __name__ == "__main__":
    main()