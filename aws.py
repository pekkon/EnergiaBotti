import boto3
from botocore.exceptions import ClientError

def update_records(timestamppi, value, taulu='tuulituotanto', avain="this"):
    return None
    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table(taulu)

    response = table.update_item(
        Key={
            'highest': avain
        },
        UpdateExpression="set ajankohta=:t, arvo=:v",
        ExpressionAttributeValues={
            ':t': timestamppi,
            ':v': value
        },
        ReturnValues="UPDATED_NEW"
    )
    return response


def get_records(dynamodb=None, taulu='tuulituotanto', avain="this"):
    return 1,1
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table(taulu)

    try:

        response = table.get_item(Key={'highest': avain})

    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        timestamp = response['Item']['ajankohta']
        value = response['Item']['arvo']
        return timestamp, value