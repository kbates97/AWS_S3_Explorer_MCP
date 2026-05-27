import pytest
from unittest.mock import AsyncMock, patch
from botocore.exceptions import ClientError
from s3_mcp_server import list_s3_buckets, list_s3_objects, read_s3_file_head

@pytest.mark.asyncio
# Intercept the S3 client creation to return a mock client
@patch('s3_mcp_server.session.create_client')
async def test_list_s3_buckets_success(mock_create_client):
    """Test that a successful bucket list response is correctly parsed."""

    # Mock the S3 client and its response
    mock_client = AsyncMock()
    mock_client.list_buckets.return_value = {
        'Buckets': [{'Name': 'bucket1'}, {'Name': 'bucket2'}]
    }
    # Set the mock to be returned when the context manager is entered
    mock_create_client.return_value.__aenter__.return_value = mock_client
    
    # Call the function being tested
    result = await list_s3_buckets()

    # Assert that the result is as expected
    assert result == ['bucket1', 'bucket2']
    mock_client.list_buckets.assert_called_once()

@pytest.mark.asyncio
@patch('s3_mcp_server.session.create_client')
async def test_list_s3_buckets_client_error(mock_create_client):
    """Test error handling when AWS credentials are invalid."""
    
    # Mock the S3 client to raise a ClientError when list_buckets is called
    mock_client = AsyncMock()
    mock_client.list_buckets.side_effect = ClientError(
        error_response={'Error': {'Code': 'AuthFailure', 'Message': 'Invalid credentials'}},
        operation_name='ListBuckets'
    )
    mock_create_client.return_value.__aenter__.return_value = mock_client
    
    # Call the function being tested
    result = await list_s3_buckets()

    # Assert that the error message is returned in the expected format
    assert len(result) == 1
    assert result[0].startswith("Error accessing S3")
    assert "Invalid credentials" in result[0]
    mock_client.list_buckets.assert_called_once()

@pytest.mark.asyncio
@patch('s3_mcp_server.session.create_client')
async def test_list_s3_buckets_empty(mock_create_client):
    """Test that an empty bucket list is handled correctly."""
    
    # Mock the S3 client to return an empty bucket list
    mock_client = AsyncMock()
    mock_client.list_buckets.return_value = {'Buckets': []}
    mock_create_client.return_value.__aenter__.return_value = mock_client
    
    # Call the function being tested
    result = await list_s3_buckets()

    # Assert that the result is an empty list
    assert result == []
    mock_client.list_buckets.assert_called_once()

@pytest.mark.asyncio
@patch('s3_mcp_server.session.create_client')
async def test_list_s3_objects_success(mock_create_client):
    """Test that a successful object list response is correctly parsed."""
    
    # Mock the S3 client and its response
    mock_client = AsyncMock()
    mock_client.list_objects_v2.return_value = {
        'Contents': [
            {'Key': 'file1.csv', 'Size': 1234, 'LastModified': '2026-01-01T00:00:00Z'},
            {'Key': 'file2.csv', 'Size': 5678, 'LastModified': '2026-01-02T00:00:00Z'}
        ]
    }
    mock_create_client.return_value.__aenter__.return_value = mock_client
    
    # Call the function being tested
    result = await list_s3_objects(bucket_name='test-bucket')

    # Assert that the result is as expected
    assert len(result) == 2
    assert result[0]['key'] == 'file1.csv'
    assert result[0]['size_bytes'] == 1234
    assert result[0]['last_modified'] == '2026-01-01T00:00:00Z'
    assert result[1]['key'] == 'file2.csv'
    assert result[1]['size_bytes'] == 5678
    assert result[1]['last_modified'] == '2026-01-02T00:00:00Z'
    mock_client.list_objects_v2.assert_called_once_with(Bucket='test-bucket', Prefix='', MaxKeys=50)

@pytest.mark.asyncio
@patch('s3_mcp_server.session.create_client')
async def test_list_s3_objects_client_error(mock_create_client):
    """Test error handling when the specified bucket does not exist."""
    
    # Mock the S3 client to raise a ClientError when list_objects_v2 is called
    mock_client = AsyncMock()
    mock_client.list_objects_v2.side_effect = ClientError(
        error_response={'Error': {'Code': 'NoSuchBucket', 'Message': 'The specified bucket does not exist'}},
        operation_name='ListObjectsV2'
    )
    mock_create_client.return_value.__aenter__.return_value = mock_client
    
    # Call the function being tested
    result = await list_s3_objects(bucket_name='nonexistent-bucket')

    # Assert that the error message is returned in the expected format
    assert len(result) == 1
    assert 'error' in result[0]
    assert result[0]['error'].startswith("Error accessing bucket nonexistent-bucket")
    assert "The specified bucket does not exist" in result[0]['error']
    mock_client.list_objects_v2.assert_called_once_with(Bucket='nonexistent-bucket', Prefix='', MaxKeys=50)

@pytest.mark.asyncio
@patch('s3_mcp_server.session.create_client')
async def test_read_s3_file_head_success(mock_create_client):
    """Test that a successful get_object response is correctly parsed."""
    
    # Mock the S3 client and its response
    mock_client = AsyncMock()
    mock_client.get_object.return_value = {
        'Body': AsyncMock(read=AsyncMock(return_value=b'header1,header2\nvalue1,value2\n'))
    }
    mock_create_client.return_value.__aenter__.return_value = mock_client
    
    # Call the function being tested
    result = await read_s3_file_head(bucket_name='test-bucket', object_key='test-file.csv')

    # Assert that the result is as expected
    assert result == 'header1,header2\nvalue1,value2\n'
    mock_client.get_object.assert_called_once_with(Bucket='test-bucket', Key='test-file.csv', Range='bytes=0-2000')

@pytest.mark.asyncio
@patch('s3_mcp_server.session.create_client')
async def test_read_s3_file_head_client_error(mock_create_client):
    """Test error handling when the specified object does not exist."""
    
    # Mock the S3 client to raise a ClientError when get_object is called
    mock_client = AsyncMock()
    mock_client.get_object.side_effect = ClientError(
        error_response={'Error': {'Code': 'NoSuchKey', 'Message': 'The specified key does not exist'}},
        operation_name='GetObject'
    )
    mock_create_client.return_value.__aenter__.return_value = mock_client
    
    # Call the function being tested
    result = await read_s3_file_head(bucket_name='test-bucket', object_key='nonexistent-file.csv')

    # Assert that the error message is returned in the expected format
    assert result.startswith("Error reading file nonexistent-file.csv")
    assert "The specified key does not exist" in result
    mock_client.get_object.assert_called_once_with(Bucket='test-bucket', Key='nonexistent-file.csv', Range='bytes=0-2000')