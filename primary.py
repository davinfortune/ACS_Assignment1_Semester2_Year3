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
    ec2client = boto3.client(
    'ec2',
    aws_access_key_id = accessKeyId,
    aws_secret_access_key = secretAccessKey
    )

    print("We Patched You In!")

def mainMenu():

    print("Main Menu")
    print("---------")
    print("1. Create A New Instance")
    print("2. Start/Stop an Instance")
    print("3. Upload an Image")
    print("---------")
    userSelection = input("Your Selection : ")
    switcher={
        # 1: createNewInstance(),
        # 2: startStopper(),
        # 3: uploadImage()
    }
    return switcher.get(userSelection,"Invalid Number Selected")
    
awsApiKey()
mainMenu()


    