import rpyc
import sys
import os
import pymongo
import pprint
import random, math
import string
import Crypto
from Crypto.PublicKey import RSA
list_paths = ['a']
class UserService(rpyc.Service):
	def on_connect(self, connection):
		pass

	def on_disconnect(self, connection):
		pass
	def create_user(self,user_or_group, userid,base_path):
		os.mkdir(base_path+"/"+userid)
		list_paths = [base_path+"/"+userid]
		v = 8

		while(len(list_paths)>0 and len(list_paths)<=pow(v,5)):
			parent = list_paths.pop(0)
			print parent
			pwd = parent
			size = 128
			f = open(pwd+"/"+"file", "wb")
			c = open(pwd+'/config','wb')
			f.seek(size-1)
			f.write(b"\0")
			f.close()
			c.close()

			if len(parent.split("/"))<10:
				for k in range(v):
					os.mkdir(parent+"/"+str(k+1))
					list_paths.append(parent+"/"+str(k+1))

		list_paths = []
		return 0

	def exposed_register_user(self, username, password):
		uri = "mongodb://HarshVardhanKumar:HarshVardhanKumar1@ds241298.mlab.com:41298/securityproject"
		client = pymongo.MongoClient(uri, retryWrites=False)
		db = client["securityproject"]
		login = db["login_data"]
		login_dat = login.find()
		client.close()
		p = None
		try:
			p = random.SystemRandom().randint(1025,pow(2,32)-1)
			#print 'random generated'
			for data in login_dat:
				if data["userid"] == str(p):
					p = random.SystemRandom().randint(1025, pow(2,32)-1)
			#		print 'match found, regenerating'
					continue
		except:
			return "Not available.."

		try:
			client = pymongo.MongoClient(uri,retryWrites=False)
			post = {"userid":str(p), "password": password}
			login = client['securityproject']

			login = login['login_data']
			idi = login.insert_one(post)
			global base_path
			os.mkdir(base_path+"/"+str(p))

			list_paths = [base_path+"/"+str(p)]
			v = 32

			while(len(list_paths)>0 and len(list_paths)<=pow(v,5)):
				parent = list_paths.pop(0)
				pwd = parent
				size = 128
				f = open(pwd+"/"+"file", "wb")
				v = 32

				f.seek(size-1)
				f.write(b"\0")
				f.close()
				c.close()

				if len(parent.split("/"))<8:
					for k in range(v):
						os.mkdir(parent+"/"+str(k+1))
						list_paths.append(parent+"/"+str(k+1))

			list_paths = []
			client.close()
		except :
			client.close()
			return "error"
		del login
		del client
		del db
		return p

	def exposed_register_group(self, admin, password,group_name):
		# verify if the admin is a valid user
		uri = "mongodb://HarshVardhanKumar:HarshVardhanKumar1@ds241298.mlab.com:41298/securityproject"
		client = pymongo.MongoClient(uri, retryWrites=False)
		db = client["securityproject"]
		login = db["login_data"]
		login_dat = login.find()

		try:
			if login.count_documents({"userid":admin,"password":password}) == 1:
				# the admin is a valid user
				# create_user("group", admin)
				print ()
		except:
			del login
			del client
			del login_dat
			return "operation failed. Try again."
		del login
		del client
		del login_dat
		del db
		client.close()
		return 0


#	def on_connect(self,connection):
		# check if the user is authenticated by Login Servic
#		print("User Service Connected")

#	def on_disconnect(self,connection):
#		pass

	def find_paths(value,userid):
		n = 32
		level = 50
		path = ""
		while level>1 :
			level = int(math.floor(math.log(((n-1)*(value+1)+1), n)))
			position = (((value - ((pow(n,level)-1)/(n-1)-1)) % n))
			if position == 0:
				position = n
			path = str(position)+"/"+path
			value = int(math.floor((value-1)/n))
		global base_path
		path = base_path+"/"+str(userid)+"/"+path
		return path

	def exposed_file_upload_user(self, userid, filee, file_sequence):
		# see if the user is already authenticated

		# filee is a file string
		global authenticated_users
		if not userid in authenticated_users:
			return "authentication failed"
		size = len(file_sequence)

		for a in range(size):
			#path = find_paths(file_sequence[a], userid)
			value = file_sequence[a]
			#print 'value is :'+str(value)
			n = 32
			level = 50
			path = ""
			while level>1 :
				level = int(math.floor(math.log(((n-1)*(value+1)+1), n)))
				position = (((value - ((pow(n,level)-1)/(n-1)-1)) % n))
			#	print 'position is :'+str(position)
				if position == 0:
					position = n
				path = str(position)+"/"+path
				value = int(math.floor((value-1)/n))
			global base_path
			path = base_path+"/"+str(userid)+"/"+path
			#print path+'file'
			try:
				with open(path+"file", "wb") as fil:
					print a
					print filee[a:a+127]
					fil.write(filee[a*127:a*127+127])

			except:
				return "error"
		return "okay"

	def exposed_file_read_user(self, userid, file_sequence):
		global authenticated_users
		if not userid in authenticated_users:
			return "authentication_failed"
		size = len(file_sequence)
		filee = ""
		for a in range(size):
			#path = find_paths(file_sequence[a],userid)
			value = file_sequence[a]
			n = 4
			level = 50
			path = ""
			while level>1 :
				level = int(math.floor(math.log(((n-1)*(value+1)+1), n)))
				position = (((value - ((pow(n,level)-1)/(n-1)-1)) % n))
				if position == 0:
					position = n
				path = str(position)+"/"+path
				value = int(math.floor((value-1)/n))
			global base_path
			path = base_path+"/"+str(userid)+"/"+path

			try:
				with open(path+"file", "rb") as fil:
					filee = filee+fil.read()[:-1]
			except:
				return "error"
		filee = filee+"/0"
		return filee

	def exposed_file_delete_user(self, userid, file_sequence):
		global authenticated_users
		if not userid in authenticated_users:
			return "authentication_failed"
		size = len(file_sequence)
		for a in range(size):
			value = file_sequence[a]

			n = 4
			level = 50
			path = ""
			while level>1 :
				level = int(math.floor(math.log(((n-1)*(value+1)+1), n)))
				position = (((value - ((pow(n,level)-1)/(n-1)-1)) % n))
				if position == 0:
					position = n
				path = str(position)+"/"+path
				value = int(math.floor((value-1)/n))
			global base_path
			path = base_path+"/"+str(userid)+"/"+path
			print path
			try:
				key = RSA.generate(2048)
				binPrivKey = key.exportKey('DER')
				binPubKey = key.publickey().exportKey('DER')
				privKeyObj = RSA.importKey(binPrivKey)
				pubKeyObj = RSA.importKey(binPubKey)
				print 'rsa generrea'
				with open(path+"file", "wb") as filee:
					filee.write(privKeyObj.encrypt(''.join(random.SystemRandom().choice(string.ascii_lowercase+string.ascii_uppercase+string.digits) for i in range(127))))
			except:
				return 'error'
		return "file deleted"

	def exposed_authenticat(self,userid, password):
		client = pymongo.MongoClient("mongodb://HarshVardhanKumar:HarshVardhanKumar1@ds241298.mlab.com:41298/securityproject")
		db = client["securityproject"]
		login = db["login_data"]
		print(db.list_collection_names())
		#p = random.SystemRandom().randint(1025,pow(2,16)-1)
		try:
			if login.count_documents({"userid":userid, "password":password})==1:
				print("document found")
				global authenticated_users
				authenticated_users.append(userid)
				del login
				del db

		except:
			del login
			del client
			print("exception occured")
			return "error"
		client.close()
		return "authenticated"

	def exposed_logout(self, userid, password):
		client = pymongo.MongoClient("mongodb://HarshVardhanKumar:HarshVardhanKumar1@ds241298.mlab.com:41298/securityproject")
		db = client["securityproject"]
		login = db["login_data"]
		#print(db.list_collection_names())
		#p = random.SystemRandom().randint(1025,pow(2,16)-1)
		try:
			if login.count_documents({"userid":userid, "password":password})==1:
				print("document found")
				global authenticated_users
				authenticated_users.remove(userid)
				del login
				del db
				del client
		except:
			del login
			del client
			print("exception occured")
			return "error"
		client.close()
		return "logout"

if __name__ == "__main__":
	authenticated_users = ['a']
	list_paths = []
	nodes = 4

	base_path = sys.argv[1]+"/rooot"
	group_path = base_path+'/shared'
	if not os.path.isdir(base_path):
		os.mkdir(base_path)
	if not os.path.isdir(group_path):
		os.mkdir(group_path)
	u = UserService()
	u.create_user('group','shared',group_path)

	from rpyc.utils.server import ThreadedServer

	#t = ThreadedServer(MyService, port = 1800)
	t = ThreadedServer(UserService,port = 15892)
	#l = ThreadedServer(LoginService, port = 1780)
	t.start()
	#l.start()
	#t.start()
