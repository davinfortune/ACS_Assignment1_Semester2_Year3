import boto3
import botocore
import json

# AWS API KEYS
def awsApiKey():

    try:
        with open('credentials.txt') as json_file:
            data = json.load(json_file)
            for user in data['credentials']:
                accessKeyId = user['aws_access_key_id']
                secretAccessKey = user['aws_secret_access_key']
    except:
        print("\nWe Have No Credentials Stored for you!")
        print("\nEnter Your Details Below -\n")
        userAccessKey = input("Please Enter Your AWS Access Key Id : ")
        userSecretAccessKey = input("Please Enter Your AWS Secret Access Key : ")
        credentialsVerifier = boto3.client(
        'sts',
        aws_access_key_id = userAccessKey,
        aws_secret_access_key = userSecretAccessKey
        )
        # THIS CODE WAS RECIEVED FROM THJE FOLLOWING LINK : https://stackoverflow.com/questions/53548737/verify-aws-credentials-with-boto3
        try:
            credentialsVerifier.get_caller_identity()
            accessKeyId = userAccessKey
            secretAccessKey = userSecretAccessKey
        except botocore.exceptions.ClientError:
            print("Your Credentials Are not Correct")
            quit()
        # THIS CODE WAS RECIEVED FROM THE FOLLOWING LINK : https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
        data = {}
        data['credentials'] = []
        data['credentials'].append({
            'aws_access_key_id' : accessKeyId,
            'aws_secret_access_key' : secretAccessKey
        })
        with open('credentials.txt', 'w') as outfile:
            json.dump(data, outfile)
    


    # THIS CODE WAS RECIEVED FROM THE BOTO3 DOCUMENTATION : https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
    global ec2client 
    ec2client = boto3.resource('ec2',aws_access_key_id = accessKeyId,aws_secret_access_key = secretAccessKey)
    print("We Patched You In!")
    return ec2client

def createNewInstance():
    # THE FOLLOWING CODE WAS TAKEN FROM THE BOTO3 DOCUMENTATION : https://boto.readthedocs.io/en/latest/ref/ec2.html#boto.ec2.connection.EC2Connection.run_instances
    key_pair_name = input("Please Enter a Name for your Key : ")
    # instance_name = input("Please Enter a Name for your Instance : ")
    try :
        ec2client.create_key_pair(KeyName = key_pair_name)
    except botocore.exceptions.ClientError :
        print("\n Key Already Exists \n")
    print("Pending......")
    user_data = '''#!/bin/bash
    sudo yum install httpd -y
    sudo systemctl enable httpd
    sudo systemctl start httpd'''
    
        
    currentInstance = ec2client.create_instances(ImageId='ami-096f43ef67d75e998', MinCount=1, MaxCount=1, InstanceType='t2.nano',KeyName=key_pair_name,UserData = user_data)
    currentInstance.create_security_group(GroupName = 'HTTP',Description='ALLOWING ACCESS THROUGH THE INTERNET')
    print("Your Instance Has Been Created!")
    


def mainMenu():

    print("Main Menu")
    print("---------")
    print("1. Create A New Instance")
    print("2. Start/Stop an Instance")
    print("3. Upload an Image")
    print("4. Upload an Image")
    print("---------")
    userSelection = input("Your Selection : ")
    switcher={
        1: createNewInstance()
        # 2: startStopper(),
        # 3: uploadImage()
    }
    return switcher.get(userSelection,"Invalid Number Selected")

    
awsApiKey()
mainMenu()


    