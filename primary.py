import boto3
import botocore
import json
import urllib.request
import os
import subprocess

# AWS API KEYS/ LOGIN SYSTEM
def awsApiKey():
    # TRYING TO SEE IF THE CREDENTIALS ARE ALREADY STORED, IF THEY ARE THE USER HAS NO REASION TO ENTER THEM AGAIN
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
        # I USE AMAZON AUTHENTICATION SERVICE TO SEE IF THE CREDENTIALS EXIST
        try:
            credentialsVerifier.get_caller_identity()
            accessKeyId = userAccessKey
            secretAccessKey = userSecretAccessKey
        except botocore.exceptions.ClientError:
            print("Your Credentials Are not Correct")
            quit()
        # THIS CODE WAS RECIEVED FROM THE FOLLOWING LINK : https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
        # HERE I WRITE OUT THE USERS CREDENTIALS TO A JSON FILE SO I HAVE PERSISTANCE ON THE USER
        data = {}
        data['credentials'] = []
        data['credentials'].append({
            'aws_access_key_id' : accessKeyId,
            'aws_secret_access_key' : secretAccessKey
        })
        with open('credentials.txt', 'w') as outfile:
            json.dump(data, outfile)
    


    # THIS CODE WAS RECIEVED FROM THE BOTO3 DOCUMENTATION : https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
    # HERE I LOG IN TO ALL OF THE BOTO3 RESOURCES/CLIENTS I WILL NEED IN ORDER FOR MY SYSTEM TO WORK
    global ec2client 
    global s3client
    ec2client = boto3.resource('ec2',aws_access_key_id = accessKeyId,aws_secret_access_key = secretAccessKey)
    s3client = boto3.client('s3',aws_access_key_id = accessKeyId,aws_secret_access_key = secretAccessKey)
    print("\nWe Patched You In!")
    return ec2client

def createNewInstance():
    # THE FOLLOWING CODE WAS TAKEN FROM THE BOTO3 DOCUMENTATION : https://boto.readthedocs.io/en/latest/ref/ec2.html#boto.ec2.connection.EC2Connection.run_instances
    # I GET THE USER TO ENTER IN THE NAME FOR THERE KEY AND USE A WHILE LOOP TO MAKE SURE THE KEY IS ENTERED CORRECTLY
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

    # PREPARING USER DATA
    user_data = '''
    #!/bin/bash
    yum update -y
    yum install httpd -y
    systemctl enable httpd
    systemctl start httpd
    '''
    # CREATING A NEW INSTANCE AND ALSO MAKING SURE THE USERS SECURITY GROUP ID IS CORRECT
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
    # USING A FOR LOOP TO LIST OUT ALL THE CURRENT RUNNING INSTANCES SO THAT THE USER CAN CHOOSE ONE TO TERMINATE, ALSO USING WAITERS SO THAT THERE IS CONFIRMATION OF THE TERMINATION
    x=1
    print("\nPlease Select an Instance to Terminate\n")
    print("--------------------------------------\n")
    runningInstances = ec2client.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    for inst in runningInstances:
        print(str(x) + ". " + inst.id)
        x = x + 1
    instanceToTerminate = input("\nYour Selection: ")
    y=1
    for inst in runningInstances:
        if(y == int(instanceToTerminate)):
            print("\nTerminating.....")
            inst.terminate()
            inst.wait_until_terminated()
            break
        else:
            y = y + 1

def createNewBucket():
    # LETTING THE USER NAME THE BUCKET TO BE CREATED
    bucket_name = input("\nPlease Enter a Bucket Name : ")
    try:
        location = {'LocationConstraint': 'eu-west-1'}
        s3client.create_bucket(Bucket=bucket_name,CreateBucketConfiguration=location)
    except botocore.exceptions.ClientError:
       print("That Bucket already Exists")
    print("\nYour Bucket Has Been Created!")

def uploadImageToBucket():
    # https://witacsresources.s3-eu-west-1.amazonaws.com/image.jpg
    # LETTING THE USER CHOOSE WHAT IMAGE TO UPLOAD TO THE BUCKET THEN DOWNLOADING IT AND UPLOADING IT TO THE BUCKET
    urlEntered = input("\nPlease Enter the Url of Your Image: ")

    if os.path.exists("image.jpg"):
        os.remove("image.jpg")
        urllib.request.urlretrieve(urlEntered, "image.jpg")
    else:
        urllib.request.urlretrieve(urlEntered, "image.jpg")

    file_name = 'image.jpg'
    x=1
    allBuckets = s3client.list_buckets()
    for bucket in allBuckets['Buckets']:
        print(str(x) + ". " + bucket["Name"])
        x= x + 1
    selectedBucket = input("\nPlease Select A Bucket to Upload to: ")
    y=1
    for bucket in allBuckets['Buckets']:
        if y == int(selectedBucket):
            bucket_name = bucket["Name"]
            break
        y = y + 1
    s3client.upload_file(file_name, bucket_name, file_name,
    ExtraArgs={'ACL': 'public-read'})

def uploadImageToInstance():
    print("\nPlease Select A Bucket to get an Image from: \n")
    x=1
    allBuckets = s3client.list_buckets()
    for bucket in allBuckets['Buckets']:
        print(str(x) + ". " + bucket["Name"])
        x= x + 1
    selectedBucket = input("\nYour Selection: ")
    y=1
    for bucket in allBuckets['Buckets']:
        if y == int(selectedBucket):
            bucket_name = bucket["Name"]
            break
        y = y + 1
    objectURL = "https://%s.s3-eu-west-1.amazonaws.com/image.jpg" % (bucket_name)

    # GETTING IP ADDRESS FOR SSH COMMAND

    x=1
    print("\nPlease Select an Instance to Upload to:\n")
    print("--------------------------------------\n")
    runningInstances = ec2client.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    for inst in runningInstances:
        print(str(x) + ". " + inst.id)
        x = x + 1
    selectedInstance = input("\nYour Selection: ")
    y=1
    for inst in runningInstances:
        if(y == int(selectedInstance)):
            public_ip = inst.public_ip_address
            private_ip = inst.private_ip_address
            key_pair_name = inst.key_name + ".pem"
            break
        else:
            y = y + 1

    if os.path.exists(key_pair_name):
        pass
    else:
        print("\nYou do not have the key installed!\nPlease install the key or select a different instance!")
        mainMenu()
    # CHANGING PERMISSIONS ON THE KEY FOR USE WITH SSH
    chmodCommmand = '''icacls.exe %s /reset
    icacls.exe %s /grant:r "$($env:username):(r)"
    icacls.exe %s /inheritance:r
    ''' % (key_pair_name,key_pair_name,key_pair_name)
    subprocess.Popen(["powershell",chmodCommmand], stdout=subprocess.PIPE)
    # UPDATING THE WEBPAGE WITH THE FOLLOWING COMMANDS
    cmdHolder = "ssh -o StrictHostKeyChecking=no -i " + key_pair_name + " ec2-user@" + public_ip +  " sudo touch index.html"
    print(cmdHolder)
    subprocess.run(cmdHolder,shell=True)

    cmdHolder = "ssh -i " + key_pair_name + " ec2-user@" + public_ip + " sudo chmod 777 index.html"
    print(cmdHolder)
    subprocess.run(cmdHolder,shell=True)

    cmdHolder = "ssh -i " + key_pair_name + " ec2-user@" + public_ip +  " sudo mv index.html /var/www/html"
    subprocess.run(cmdHolder,shell=True)

    subprocess.run(['ssh','-i',key_pair_name,'ec2-user@'+public_ip,' sudo echo "<br>Private IP address: %s"' % (private_ip), ' >> /var/www/html/index.html'])

    subprocess.run(['ssh','-i',key_pair_name,'ec2-user@'+public_ip,' sudo echo "<br>Availablity Zone :" >> /var/www/html/index.html'])

    subprocess.run(['ssh','-i',key_pair_name,'ec2-user@'+public_ip,' curl http://169.254.169.254/latest/meta-data/placement/availability-zone >> /var/www/html/index.html'])

    subprocess.run(['ssh','-i',key_pair_name,'ec2-user@'+public_ip,' sudo echo "<img src = %s>"' % (objectURL),' >> /var/www/html/index.html'])
    quit()

def uploadMonitoringToInstance():
    # USER INPUT SELECTING INSTANCE
    x=1
    print("\nPlease Select an Instance to Upload to:\n")
    print("--------------------------------------\n")
    runningInstances = ec2client.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    for inst in runningInstances:
        print(str(x) + ". " + inst.id)
        x = x + 1
    selectedInstance = input("\nYour Selection: ")
    y=1
    for inst in runningInstances:
        if(y == int(selectedInstance)):
            public_ip = inst.public_ip_address
            key_pair_name = inst.key_name + ".pem"
            break
        else:
            y = y + 1

    if os.path.exists(key_pair_name):
        pass
    else:
        print("\nYou do not have the key installed!\nPlease install the key or select a different instance!")
        mainMenu()
    # CHANGING PERMISSIONS ON KEY TO BE USED WITH SSH 
    chmodCommmand = '''icacls.exe %s /reset
    icacls.exe %s /grant:r "$($env:username):(r)"
    icacls.exe %s /inheritance:r
    ''' % (key_pair_name,key_pair_name,key_pair_name)
    subprocess.Popen(["powershell",chmodCommmand], stdout=subprocess.PIPE)
    # USING SSH TO UPLOAD AND RUN MONITOR.sh ON THE INSTANCE 
    ip_combined = "ec2-user@" + public_ip

    ip_scp = ip_combined + ":~"
    subprocess.run(['scp', '-i', key_pair_name, 'monitor.sh', ip_scp])
    chmod_commad = "chmod +x monitor.sh"
    run_command = "./monitor.sh"
    subprocess.run(['ssh', '-i', key_pair_name, ip_combined, chmod_commad])
    subprocess.run(['ssh', '-i', key_pair_name, ip_combined, run_command])
    quit()

def mainMenuSwitcher(userSelection):
    intCoverter = int(userSelection)
    if intCoverter == 1:
        createNewInstance()
    elif intCoverter == 2:
        terminateInstance()
    elif intCoverter == 3:
        createNewBucket()
    elif intCoverter == 4:
        uploadImageToBucket()
    elif intCoverter == 5:
        uploadImageToInstance()
    elif intCoverter == 6:
        uploadMonitoringToInstance()
    elif intCoverter == 0:
        quit()
    else:
        print("\n!!!!! Invalid Selection !!!!!")

def mainMenu():
    print("\nMain Menu")
    print("---------")
    print("1. Create A New Instance")
    print("2. Terminate an Instance")
    print("3. Create Bucket")
    print("4. Upload an Image to a Bucket")
    print("5. Upload an Image to an Instance")
    print("6. Upload Monitoring To an Instance")
    print("\n0. Quit")
    print("---------")
    userSelection = input("Your Selection : ")
    mainMenuSwitcher(userSelection)
    return True
     
awsApiKey()
while True:
    mainMenu()


    