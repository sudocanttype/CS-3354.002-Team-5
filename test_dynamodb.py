import boto3

# Create a DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # change region if needed

# Try to list all table names
try:
    tables = list(dynamodb.tables.all())
    print("✅ Connected to DynamoDB!")
    print("Tables found:")
    for table in tables:
        print(" -", table.name)
except Exception as e:
    print("❌ Failed to connect to DynamoDB.")
    print("Error:", e)
