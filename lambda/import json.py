import json
import boto3
import hashlib

dynamodb = boto3.resource('dynamodb')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

TABLE_NAME = 'PTAssistantCache'
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        question = body.get('question', '').strip()

        if not question:
            return response(400, {'error': 'No question provided'})

        cache_key = hashlib.md5(question.lower().encode()).hexdigest()
        cached = table.get_item(Key={'query_id': cache_key}).get('Item')
        if cached:
            return response(200, {'answer': cached['answer'], 'source': 'cache'})

        claude_response = bedrock.invoke_model(
            modelId='arn:aws:bedrock:us-east-1:583010722695:inference-profile/global.anthropic.claude-haiku-4-5-20251001-v1:0',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 500,
                'messages': [{'role': 'user', 'content': question}]
            })
        )

        answer = json.loads(claude_response['body'].read())['content'][0]['text']

        table.put_item(Item={
            'query_id': cache_key,
            'question': question,
            'answer': answer
        })

        return response(200, {'answer': answer, 'source': 'bedrock'})

    except Exception as e:
        return response(500, {'error': str(e)})

def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body)
    }