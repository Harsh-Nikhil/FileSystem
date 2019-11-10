import os
from passthrough import Passthrough
# the server does not know either the user name or the file name. It only knows of userid (which is not same as username) and fileid. The mapping between the userId and the fileId with username and filename is maintained by the client software.
list_paths = []

print("hello world")

def create_user(user_or_group, userid):
	pwd = "/root"
	os.mkdir(pwd+str(userid))
	del list_paths[:]
	list_paths = [pwd+str(userid)]
	v = 32
	if user_or_group != "user":
		v = 16

	while(len(list_paths)>0 and len(list_paths)<=pow(v,5)):
		create_dirs(list_paths.pop(0))
	del list_paths[:]

def create_dirs(user_or_group,parent):
	pwd = parent
	size = 128
	f = open(pwd+"/"+"file", "wb")
	v = 32
	if user_or_group != "user":
		v = 16
		c = open(pwd+"/"+"config","w")
		c.write("0")
		c.close()
	# c will contain info whether this folder is empty or not. If not the user this folder belongs. Not required in case of users. ONly in case of groups.
	f.seek(size-1)
	f.write(b"\0")
	f.close()
	for k in range(v):
		os.mkdir(parent+"/"+str(k))
		list_paths.append(parent+"/"+str(k))


def create_file(userid,filesequence, timestamp, files):
	# files is a list of byte[] of any arbitrary size.
	# timestamp will decide where to begin
	# filesequence size is unknown. It is created by the client using some method a specific no. of times for a specific no. of bytes. Those values are then converted into their corresponding decimal equivalent. Based on these decimal equivalent, we can know the exact location of that folder in the user tree
	# filesequence is a list format

	# from the value in filesequence, you need to create the location of the folder
	parent = "/root/"+str(userid)
	for a in range(len(filesequence)):
		#lets suppose that filesequence contains the path values 
		try:
			f = open(filesequence[a]+"/file", "wb")
			f.write(files[a])
			f.close()
		except:
			return 0
	return 1

def read_files_user(userid, filesequence, timestamp):
	# no need to view if the files are in the corresponding directories or not. If wrong sequence, then you will get wrong data.
	fi= ""
	# assume that filesequence contains the path values
	for a in range(len(filesequence)):
		try:
			f = open(filesequence[a]+"/file", "rb")
			fi = fi + f.read()
			f.close()
		except: 
			return 0
	return fi














