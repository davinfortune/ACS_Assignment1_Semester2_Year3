import boto3

# AWS API KEYS
def awsApiKey(accessKeyId,secretAccessKey):
    # THIS CODE WAS RECIEVED FROM THE BOTO3 DOCUMENTATION : https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
    ec2client = boto3.client(
    'ec2',
    aws_access_key_id = accessKeyId,
    aws_secret_access_key = secretAccessKey
    )
    print("Your Patched In!")

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
    
userAccessKey = input("Please Enter Your AWS Access Key Id : ")
userSecretAccessKey = input("Please Enter Your AWS Secret Access Key : ")
awsApiKey(userAccessKey,userSecretAccessKey)
mainMenu()


    