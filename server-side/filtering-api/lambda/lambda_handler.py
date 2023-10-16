def handler(event, context):
    return {
        "statusCode": 200,
        "body": "Hello, World!",
        "headers": {
            "Content-Type": "text/plain"
        }
    }
