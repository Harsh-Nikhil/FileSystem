# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 16:27:44 2019

@author: nikhi
"""
#Making RSA encryption decryption work
import Crypto
import random
from Crypto.PublicKey import RSA
from Crypto import Random
from pymongo import MongoClient
import ast
import json
import math
with open("filenamelist.json",'rb') as json_file:
        json_decoded = json.load(json_file)

username="Nikhil"


filename=raw_input("enter the full path of the file name to be upload")
fileDescriptor=open(filename,'rb')
fileContent=fileDescriptor.read()
fileSize=math.ceil(fileContent/255)
count=0;
with open (username+"_publickey.txt","rb") as fd2:
    pubKey=fd2.read()
with open (username+"_privatekey.txt","rb") as fd3:
    privKey=fd3.read()
privKeyobject=RSA.importKey(privKey)
pubKeyobject=RSA.importKey(pubKey)
ListFileSequence=[]
originalList=json_decoded[username]
ifileid = random.SystemRandom().randint(1, pow(32,5)-1)


while(count<fileSize):
	count=count+1;
    d=privKeyObj.encrypt(ifileid,32)[0]%(pow(32,5)-1)+1
   # print("Encrypted value is \n"+str(d))
   if(d not in originalList):
		List.append(d)
		originalList.append(d)
	else :
		ifileid = random.SystemRandom().randint(1, pow(32,5)-1)
		d=privKeyObj.encrypt(ifileid,32)[0]%(pow(32,5)-1)+1
		List.append(d)
		originalList.append(d)
    ifileid=d;
	f = []
	a = 0
	for a in range(filesize+1):
		f.append(files[a: a+255])
		a = a+255
		

with open (username+"_publickey.txt","rb") as fd2:
    pubKey=fd2.read()
with open (username+"_privatekey.txt","rb") as fd3:
    privKey=fd3.read()

d=pubKeyobject.encrypt(files,32)

encryptedContents=[]
count =0
while(count<filesize):
	count=count+1;
	encryptedContents.append(pubKeyobject.encrypt(f[count],32))

#send it to the server
print(decry)

#print("\ntrying to see the decrypted contents :"+e)
#print(e)
