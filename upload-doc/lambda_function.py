import boto3
import re
import requests
import math
from requests_aws4auth import AWS4Auth

region = 'us-east-1'  # e.g. us-west-1
service = 'es'
credentials = boto3.Session().get_credentials()
print("Credentials:", credentials)
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
print("Credentials access key:", credentials.access_key)
print("Credentials secret key:", credentials.secret_key)

host = 'https://search-saumyaa-wam4szevzmhohptgoxtccee6va.us-east-1.es.amazonaws.com'  # the OpenSearch Service domain, e.g. https://search-mydomain.us-west-1.es.amazonaws.com
index = 'saumyaa'
datatype = '_doc'
# url = host + '/' + index + '/' + datatype

headers = {"Content-Type": "application/json"}

s3 = boto3.client('s3')
author = ''
date = ''


def listToString(s):
    str1 = ""
    for ele in s:
        if isinstance(ele, bytes):
            str1 += ele.decode('utf-8', errors='replace')  # Replace undecodable bytes with a placeholder
        else:
            str1 += str(ele)
    return str1


# Lambda execution starts here
def handler(event, context):
    for record in event['Records']:
        # Get the bucket name and key for the new file
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        # Get, read, and split the file into lines
        obj = s3.get_object(Bucket=bucket, Key=key)
        body = obj['Body'].read()
        lines = body.splitlines()
        print("lines")

        cust_id = key
        url = host + '/' + index + '/' + datatype + '/' + cust_id
        print("Key:", key)

        title = lines[0].decode('utf-8', errors='replace') if lines else "Unknown Title"
        author = lines[1].decode('utf-8', errors='replace') if len(lines) > 1 else "Unknown Author"
        date = lines[2].decode('utf-8', errors='replace') if len(lines) > 2 else "Unknown Date"

        # print("Lines is ", body.split())
        print("Lines type:", type(lines))
        print("Lines content:", lines[:5])  # Print the first 5 lines for inspection

        final_body = lines[3:]
        size = len(final_body)
        end_index = math.floor(size / 10)
        print("Size: ", size)
        print("End index: ", end_index)
        summary = final_body[1:2]
        print('The binary pdf file type is', type(final_body))
        print("Title:", title)
        print("Type of title", type(title))
        print("Author:", author)
        print("Date:", date)
        # print("Body:", final_body)
        print("Summary", summary)
        print("Type of final_body:", type(final_body))
        print("Type of body in string: ", type(listToString(final_body)))
        document = {"Title": title, "Author": author, "Date": date, "Body": listToString(final_body),
                    "Summary": summary}
        # print("Document:",document)
        r = requests.post(url, auth=awsauth, json=document, headers=headers)
        print("Response:", r.text)