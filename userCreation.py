# -*- coding: utf-8 -*-
"""
Created on Sat Nov  9 12:21:11 2019

@author: nikhi
"""

from pymongo import MongoClient

def connectionEstablishment():
    return MongoClient("mongodb://NikhilAgrawal:Nikhil12@ds241298.mlab.com:41298/securityproject", retryWrites=False)


email_id=raw_input("Enter your email id:")
password=raw_input("Enter your password:")

#----------------Input done ---------------------------------

client = connectionEstablishment()
# ---Connected to the database ------------------

db=client["securityproject"] # securityproject is database name 

pointer=db["usercredentials"] #for traversing 

#now verify that given email id exists or not 
countvalue=db.usercredentials.count_documents({"_id": email_id})
if countvalue==0:
    #its a new user, so create the new account add it to the database
    post={"_id": email_id, "password":password}
    pointer.insert_one(post)
    print("Succesfully created the user.")
else:
    #password checking 
    cursor = pointer.find({"_id": email_id})
    for document in cursor: 
        s=document.get("_password")
        if s!=password :
            print("Invalid credentials!! Try Again")
        else :
            print("Welcome back : Succesfully logged in")