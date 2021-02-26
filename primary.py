import boto3
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
        print("We Have No Credentials Stored for you!")
        print("Enter Your Details Below:")
        userAccessKey = input("Please Enter Your AWS Access Key Id : ")
        userSecretAccessKey = input("Please Enter Your AWS Secret Access Key : ")
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


    