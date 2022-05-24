from ast import Index
from http import client
from itertools import count
import boto3
import pandas as pd
import xlsxwriter

l2=[]
l3=[]
instance_id=[]
instance_name=[]
sg_name=[]
sg_id=[]
keypair=[]
instance_type=[]
instance_volume_device_name=[]
instance_voulume_id=[]

writer=pd.ExcelWriter("ec2_info.xlsx",engine="xlsxwriter")

#############===================Getting All Instances Info================================
client=boto3.client('ec2')
res=client.describe_instances()
for i in res['Reservations']:
    # print("Sg Name= ",i['NetworkInterfaces'][0]['GroupName'],"Id= ",i['NetworkInterfaces'][0]['GroupId'])
    for j in i['Instances']:
        for ln in j['BlockDeviceMappings']:
            print(ln['DeviceName'],ln['Ebs']['VolumeId'])
            for k in j['Tags']:
            # print("Instance Id=",j['InstanceId'],"Name=",k['Value'])
                for l in j['NetworkInterfaces'][0]['Groups']:
                    print("Instance Id=",j['InstanceId'],"|","Name=",k['Value'],"|","Sg Name= ",l['GroupName'],"|","Id= ",l['GroupId'],"|","Key_Pair= ",j['KeyName'],\
                        "|","InstanceType= ",j['InstanceType'])
                    instance_id.append(j['InstanceId']),instance_name.append(k['Value']),sg_name.append(l['GroupName']),sg_id.append(l['GroupId']),keypair.append(j['KeyName'])
                    instance_type.append(j['InstanceType']),instance_volume_device_name.append(ln['DeviceName']),instance_voulume_id.append(ln['Ebs']['VolumeId'])

# print(res)
volumeid=[]
volumetype=[]
volumesize=[]
volume_availability_zone=[]


#########=====================Getting All Volumes Data==============================
r1=boto3.resource('ec2')
volume=r1.volumes.all()
for z in volume:
    print("VolumeId= ",z.volume_id,"|","Volume_Type= ",z.volume_type,"|","Size= ",z.size,"|","AvailabilityZone= ",z.availability_zone)
    volumeid.append(z.volume_id),volumetype.append(z.volume_type),volumesize.append(z.size),volume_availability_zone.append(z.availability_zone)

###################==================Getting All Security Groups in a Region=====================
s1=client.describe_security_groups()
# print(s1)
print("====================All Security Groups===================")
for x in s1['SecurityGroups']:
    print("SgName= ",x['GroupName'],"|","SgId= ",x['GroupId'])
    l2.append(x['GroupName'])
    l3.append(x['GroupId'])


###########========================Getting All KeyPairs In A Region======================
k_name=[]
k_id=[]

key_pair = client.describe_key_pairs()
for lm in key_pair['KeyPairs']:
    print("KeyPairName= ",lm['KeyName'],"|","KeyPairId= ",lm['KeyPairId'])
    k_name.append(lm['KeyName']),k_id.append(lm['KeyPairId'])

###############=================Getting Available Instance Types In a Region=================
itypelist=[]
itype=client.describe_instance_types()
for lk in itype['InstanceTypes']:
    # print(lk['InstanceType'])
    itypelist.append(lk['InstanceType'])
a=len(itypelist)
print(a)

#############=============List Out AllOnstance types In a Region==============================
aitypes=[]
def ec2_instance_types(region_name):
    '''Yield all available EC2 instance types in region <region_name>'''
    ec2 = boto3.client('ec2', region_name=region_name)
    describe_args = {}
    while True:
        describe_result = ec2.describe_instance_types(**describe_args)
        yield from [i['InstanceType'] for i in describe_result['InstanceTypes']]
        if 'NextToken' not in describe_result:
            break
        describe_args['NextToken'] = describe_result['NextToken']

for ec2_type in ec2_instance_types('ap-northeast-1'):
    # print(ec2_type)
    aitypes.append(ec2_type)
print("All Instance_Types= ",len(aitypes))


############==================Creating DataFrames in Panda========================
df=pd.DataFrame({
    'SgName': l2,
    'SgId': l3
})

df1=pd.DataFrame({
    "InstanceId": instance_id,
    "InstanceName": instance_name,
    "SgName": sg_name,
    "SgId": sg_id,
    "keyPair": keypair,
    "InstanceType": instance_type,
    "InstanceVolumeDeviceName": instance_volume_device_name,
    "InstanceVolumeId": instance_voulume_id

})
df2=pd.DataFrame({
    "VolumeId": volumeid,
    "Volume_Type": volumetype,
    "Volume_size": volumesize,
    "AvailabilityZone": volume_availability_zone
})
df3=pd.DataFrame({
    "KeyPairName": k_name,
    "KeyPairId": k_id
})
df4=pd.DataFrame({"InstanceTypes":itypelist })
df5=pd.DataFrame({ "InstanceTypes": aitypes})


#############=============Writing Excel Sheets using DataFrames of Pandas================
df.to_excel(writer, sheet_name='AllSecurityGroups',index=False)
df1.to_excel(writer, sheet_name="Ec2Info", index=False)
df2.to_excel(writer, sheet_name="AllVolumes", index=False)
df3.to_excel(writer, sheet_name="All KeyPairs in Region", index=False)
df4.to_excel(writer, sheet_name="Available Instance Types", index=False)
df5.to_excel(writer, sheet_name="All InstanceTypes in Region",index=False)


writer.save()
# print(l2,l3)