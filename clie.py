# this is the client file which will run on the user side and will use RPC methods to communicate with the server.py (files.py) module.
# used for: registering an user, creating a group, adding user to a group, creating files, accessing files, deleting files.
import os
import random
import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random
import time 

# try to define some server and client contract such that if anything malicious occurs at the server, next time the client connects it will know that something is malicious
userid = "" 
binPrivKey = ""
binPubKey = ""

def __init__():
	#verify if the pub/priv key is still there or not. If deleted, then the user needs to be deleted. It needs to be re-registered again.
	try:
		with open(os.getcwd()+"/.fss/pubkey", "rb") as pubkey:
			if len(pubkey.read()) == 0 :
				reply = raw_input("The user will get deleted. The key-pair has been modified.\n Do you want to get re-registered? [y/n]. All your files will get deleted anyway\n")
				if reply == 'y' or reply == "Y":
					register_user()
			#start_delete_user(userid)
	except:
		print("Some error occured. Try again")
		return


def register_user():
	# let this operation occur automatically, the first time this software is called on a client machine. 
	#The userid is completely random and the mapping between this machine and the userid is maintained using MongoDB tables running at some other server. Or, if not possible, let the client create a folder of its own and save the sensitive data corresponding to this client on the local machine.

	os.mkdir(os.getcwd()+"/.fss")
	f = open(os.getcwd()+"/.fss/userid", "wb")
	global userid = random.SystemRandom().randint(1, pow(2,256))

	pubkey = open(os.getcwd()+"/.fss/pubkey", "wb")
	prikey = open(os.getcwd()+"/.fss/prikey", "wb")
	if len(pubkey.read())==0:
		# need to create a new pub/priv key pair
		key = RSA.generate(2048)
		global binPrivKey = key.exportKey('DER')
		global binPubKey = key.publickey().exportKey('DER')
		pubkey.write(binPubKey)
		prikey.write(binPrivKey)
		global binPrivKey = ""
		global binPubKey = ""
	else:
		# read the public key of the client
		with open(os.getcwd()+"/.fss/pubkey", "rb") as privatefile:
    			global binPubKey = privatefile.read()

	password = raw_input("Select a password: \n")
	# now, store the hash of the userid and password locally. 
	# Before storing the userid and password, request server.py to check if the username and password are indeed available.
	
	# < call server method to check if the userid is available or not >
	# since the username should not be known to the server admin, there has to be a mapping between the provided username and the username seen by the server file system. we may use hash for this purpose.

	# if the selected username is available
	f.write(userid)
	f.close()
	# no need to save password locally. The password would've already been saved by the server.py module.

	return 0

def login_user():
	username = raw_input("Enter your username: ")
	password = raw_input("Enter your password: ")
	# check_username_password(username, password)
	# if match found from the module
	# load the public key of the client from the file "/.fss/pubkey"
		# return 0
	# else
		# print("Match not found. Try again...")

def upload_file():
	path = raw_input("Enter full file path: ")
	f = open(path, "rb")
	files = f.read()
	f.close()
	del f
	
	size = len(files)/255 # no. of file parts
	# now, generate that many different sequences
	
	ifileid = random.SystemRandom().randint(1, pow(32,5)-1)
	fileseqs = []
	# now starts the file sequences
	for i in range(size+1):
		fileid = binPubKey.encrypt(ifileid)%(pow(32,5)-1)+1
		fileseqs.append(fileid)
	timestamp = time.time()
	f = []
	a = 0
	for i in range(size+1):
		f.append(files[a: a+256])
		a = a+256
	
	# now call the service in server.py to upload the files into the filesystem.
	# if uploaded successfully, then save the ifileid in mongoDb server corresponding to the path value. This path value will be useful when deleting the same file. In that case, the server/client will not be aware of the ifileid value.
	# save_mongodb(path, ifileid)
	# file_upload_server(path, ifileid, f, fileseqs)
	del path
	del ifileid
	return 0
	
def delete_file():
	path = raw_input("Enter full path name: ")
	# check if this path actually exists in that user's domain using the MongoDb file lists. The check can be performed by the server's separate service and returned.
	# if true:
		# the fileserver returns the ifileid and filesize of the path.
		# the filesize of that path should be stored locally by the client
		# ifileid = get_ifileid(path)
		# now, follow the same encrypting sequence
		# fileseqs = []
		#for i in range(size+1):
			#fileid = binPubKey.encrypt(ifileid)%(pow(32,5)-1)+1
			#fileseqs.append(fileid)
		#timestamp = time.time()
		# delete_file_server(path, fileseq)

def list_files():
	#shows the list of files uploaded by the server/group. The MongoDb will store only the file path and the ifileid value. However, the attacker will still be unable to guess the file path sequence since the sequence was already encrypted. The ifileid value was encrypted and then the sequence was obtained, hence even if the attacker will know the ifileid value, it will not know the complete sequence of the file 
	#seqs = get_list_files_server(userid)
	# print(seqs)
