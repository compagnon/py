#!/usr/bin/env python

    # Use the AWS SDK for Python (Boto3) to create an Amazon Simple Storage Service
    # (Amazon S3) resource and list the buckets in your account.
    # This example uses the default settings specified in your shared credentials
    # and config files.

#  install the AWS python library: boto3
# read https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#installation
#
#
# checklist: 
#     settings of authentication/ authorization in files: ~/.aws/config and ~/.aws/credentials
#
# PS C:\Users\guillaume.compagnon\.aws> cat .\config
# [default]
# "region=eu-west-3

# PS C:\Users\guillaume.compagnon\.aws> cat .\credentials
# [default]
# aws_access_key_id = AKIA5XXXXXXXXXXXXXX
# aws_secret_access_key = Z___________________________/5k


import boto3


def list_s3_buckets(s3):
    print("Hello, Amazon S3! Let's list your buckets:")
    response = s3.list_buckets()
    
    for bucket in response['Buckets']:
        print(f"\t{bucket['Name']}")


def s3_bucket_content(s3,bucketName):
    print("Hello, Amazon S3! Let's list bucket : {0}".format(bucket_name))
    # List the objects in the bucket
    response = s3.list_objects_v2(Bucket=bucketName)

    # Iterate over the objects and print their names
    for obj in response['Contents']:
        print("{0} at last modified date {1} | size in kB: {2}".format(obj['Key'],obj['LastModified'].strftime("%d/%m/%Y %H:%M:%S") ,obj['Size']/1024))


# Create an S3 client for the region Paris - the credentials must not be set here but in ~/.aws/credentials
s3_ressource = boto3.client('s3',region_name="eu-west-3")


if __name__ == "__main__":

    #for bucket in s3_ressource.buckets.all():
    #    print(f"\t{bucket.name}")
    list_s3_buckets(s3_ressource)
      
    # Specify the bucket name
    bucket_name = 'compagnon-testpython'
    
    #list the files into the bucket
    s3_bucket_content(s3_ressource,bucket_name)
    
    file_name = 'loreal-grasp-export (1).csv'
    
    #Get the content of the  from AWS S3 and copy it as a file 
    #s3_ressource.download_file(bucket_name, file_name, r'C:\Users\guillaume.compagnon\Downloads\grasp-export.csv')
    
    destination_object_name =  r'C:\Users\guillaume.compagnon\Downloads\temp.csv'
    # print the content of a file 
    with open(destination_object_name, 'wb') as f:
        s3_ressource.download_fileobj(bucket_name, file_name, f)
        
    # open the ^destination file in read and print content
    with open(destination_object_name, 'r') as file:
        content = file.read()
        print(content)