from pprint import pprint
import json

#file delete
# finidng the key and setting the value as "None" for the deletion 
def list_of_files(username):
    if os.path.exists(username+"_files.json"):
	    with open(username+"_files.json",'rb') as fd :
		    jdata=json.load(fd) 
		    for key,value in jdata.items():
			    if value!="None":
				    print("\n"+key)
#list_of_files("nikhil")


username="Nikhil"
def updatelist(list_nodes,username):
     json_data=open("filenamelist.json")
     jdata = json.load(json_data)
     originalList=jdata[username]
     lists=list(set(originalList)-set(list_nodes))

     jdata[username]=lists
     print(str(lists))
     with open("filenamelist.json",'wb') as fd1:
	 json.dump(jdata,fd1)
   
     
def file_delete(username,filename):
    json_data=open(username+"_files.json")
    jdata = json.load(json_data)
    for key, value in jdata.items():
        if key==filename:
            list_nodes=value
            updatelist(list_nodes,username)
            print(list_nodes)
        #statement for sending it to the server and after that 
            jdata[key]="None"
    with open(username+"_files.json",'wb') as fd1:
	json.dump(jdata,fd1)
filename=raw_input("Enter the filename to be deleted :")        
file_delete(username,filename)
#for file access 
#for key, value in jdata.items():
 #   if key==Filename:
	#    FileId=value;


#for file insert        