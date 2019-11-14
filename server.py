import rpyc
import sys
import pymongo
import pprint
import random, math
import string
import Crypto
from Crypto.PublicKey import RSA

authenticated_users = ["user1"]
#login = None

class UserService(rpyc.Service):
	def on_connect(self, connection):
		pass
	
	def on_disconnect(self, connection):
		pass
		
	def exposed_register_user(self, username, password):
		client = pymongo.MongoClient("mongodb://HarshVardhanKumar:HarshVardhanKumar1@ds241298.mlab.com:41298/securityproject")
		db = client["securityproject"]
		login = db["login_data"]
		'''login_dat = login.find()
		p = None
		try:
			p = random.SystemRandom().randint(1025,pow(2,32)-1)
			for data in login_dat:
				if data["userid"] == str(p):
					p = random.SystemRandom().randint(1025, pow(2,32)-1)
					continue
		except:
			print("error")
		'''
		try:
			p = random.SystemRandom().randint(1025, pow(2,32)-1)
			post = {"userid":str(p), "password": password}
			print(post)
			idi = login.insert_one(post)
		except :
			#return "not possible. Try again..."
			print("exception occured")
			return "error"
		del login
		del client
		del db
		return p

#	def on_connect(self,connection):
		# check if the user is authenticated by Login Servic
#		print("User Service Connected")

#	def on_disconnect(self,connection):
#		pass

	def find_paths(value,userid):
		n = input("enter n: \n")
		level = 50
		path = ""
		while level>1 :
			level = int(math.floor(math.log(((n-1)*(value+1)+1), n)))
			position = (((value - ((pow(n,level)-1)/(n-1)-1)) % n))
			if position == 0:
				position = n
			path = str(position)+"/"+path
			value = int(math.floor((value-1)/n))
		
		path = "/root/"+str(userid)+"/"+path
		return path

	def exposed_file_upload_user(self, userid, filee, file_sequence):
		# see if the user is already authenticated
		if not userid in authenticated_users:
			return "authentication failed"
		size = len(file_sequence)
		for a in range(size):
			path = find_paths(file_sequence[a], userid)
			try:
				with open(path+"/file", "wb") as fil:
					fil.write(filee[a:a+127])
			except:
				return "error"
		return "okay"
	
	def exposed_file_read_user(self, userid, file_sequence):
		if not userid in authenticated_users:
			return "authentication_failed"
		size = len(file_sequence)
		filee = ""
		for a in range(size):
			path = find_paths(file_sequence[a],userid)
			try:
				with open(path+"/file", "rb") as fil:
					filee = filee+fil.read()[:-1]
			except:
				return "error"
		filee = filee+"/0"
		return filee

	def exposed_file_delete_user(self, userid, file_sequence):
		if not userid in authenticated_users:
			return "authentication_failed"
		size = len(file_sequence)
		for a in range(size):
			path = find_paths(file_sequence[a], userid)
			try:
				key = RSA.generate(2048)
				binPrivKey = key.exportKey('DER')
				binPubKey = key.publickey().exportKey('DER')
				privKeyObj = RSA.importKey(binPrivKey)
				pubKeyObj = RSA.importKey(binPubKey)

				with open(path+"/file", "wb") as filee:
					filee.write(privKeyObj.encrypt(''.join(choice() for i in range(127))))
			except:
				return 'error'
		return "file deleted"

#class LoginService(rpyc.Service):
#	def on_connect(self, connection):
#		print("connection established")

#	def on_disconnect(self, connection):
#		pass
	
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
				del client
		except:	
			del login
			del client
			print("exception occured")
			return "error"
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
		return "logout"

if __name__ == "__main__":
	#authenticated_users
	from rpyc.utils.server import ThreadedServer
	#t = ThreadedServer(MyService, port = 1800)
	t = ThreadedServer(UserService,port = 1544)
	#l = ThreadedServer(LoginService, port = 1700)
	t.start()
	#l.start()
	#t.start()
