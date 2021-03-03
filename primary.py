import boto3
import botocore
import json
import subprocess

# sg-0b6477708c0e8462d

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
    print("\nWe Patched You In!")
    return ec2client

def createNewInstance():
    # THE FOLLOWING CODE WAS TAKEN FROM THE BOTO3 DOCUMENTATION : https://boto.readthedocs.io/en/latest/ref/ec2.html#boto.ec2.connection.EC2Connection.run_instances

    while True:
        try :
            key_pair_name = input("\nPlease Enter a Name for your Key : ")
            key_file = "./%s.pem" % (key_pair_name)
            new_key_pair = ec2client.create_key_pair(KeyName = key_pair_name)
            with open(key_file, 'w') as file:
                file.write(new_key_pair.key_material)
            break
        except botocore.exceptions.ClientError :
            pass
        print("\n Key Already Exists \n")

    user_data = '''
    #!/bin/bash
    yum update -y
    yum install httpd -y
    systemctl enable httpd
    systemctl start httpd
    '''

    while True:
        try:
            user_security_group_id = input("Please Enter a Security Group Id: ")
            currentInstance = ec2client.create_instances(
                ImageId='ami-096f43ef67d75e998',
                MinCount=1,
                MaxCount=1,
                InstanceType='t2.nano',
                KeyName=key_pair_name,
                SecurityGroupIds=[user_security_group_id],
                UserData=user_data)
            break
        except botocore.exceptions.ClientError:
            pass
        print("\nYour Security Key is invalid\n")

    for inst in ec2client.instances.all():
        if inst.id == currentInstance[0].id:
            print("\nPending......")
            inst.wait_until_running()
            inst.reload()
            public_ip = inst.public_ip_address
    
    print("\nYour Instance Has Been Created!\n\nYou can Visit it Here : http://%s\n" % (public_ip))

def terminateInstance():
    x=1
    print("Please Select an Instance to Terminate\n")
    print("--------------------------------------\n")
    runningInstances = ec2client.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    for inst in runningInstances:
        print(str(x) + ". " + inst.id)
        x = x + 1
    instanceToTerminate = input("\nYour Selection: ")
    y=1
    for inst in runningInstances:
        if(y == int(instanceToTerminate)):
            print("Terminating.....")
            inst.terminate()
            inst.wait_until_terminated()
        else:
            y = y + 1

def createNewBucket():
    print("Hello")

def startStopper():
    print("Hello")

def mainMenuSwitcher(userSelection):
    intCoverter = int(userSelection)
    if intCoverter == 1:
        createNewInstance()
    elif intCoverter == 2:
        startStopper()
    elif intCoverter == 3:
        terminateInstance()
    elif intCoverter == 4:
        createNewBucket()
    # elif intCoverter == 5:
    #     uploadImage()
    elif intCoverter == 0:
        quit()
    else:
        print("\n!!!!! Invalid Selection !!!!!")

def mainMenu():
    print("\nMain Menu")
    print("---------")
    print("1. Create A New Instance")
    print("2. Start/Stop an Instance")
    print("3. Terminate an Instance")
    print("4. Create Bucket")
    print("5. Upload an Image to a Bucket")
    print("6. Upload an Image to an Instance")
    print("\n0. Quit")
    print("---------")
    userSelection = input("Your Selection : ")
    mainMenuSwitcher(userSelection)
    mainMenu()

    
awsApiKey()
mainMenu()


    