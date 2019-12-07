import os
import pyDH
import time
import rpyc
import random
import hashlib
from chacha20poly1305 import ChaCha20Poly1305
import string
import Crypto
from Crypto.PublicKey import RSA

import csv

# in a group, there is only one admin, which uploads the files. Rest of the users can only access the files.

class GroupService(rpyc.Service):
	def __init__(self, pipe, key,root):
		rpyc.Service.__init__(self)
		self.pipe = pipe
		self.secret = key # secret between the filesystem and this system
		time.sleep(15)
		self.base_path = root

		self.fileid_filename_secret_nonce_length = self.base_path+'/conf/medium.csv'
		self.filename_admin = self.base_path+'/conf/filess.csv'
		self.occupied = self.base_path+'/conf/occupied.csv'
		self.filename_listofusers = self.base_path+'/conf/abcd.csv'

		self.authenticated = []
		self.authenticated_users = {} # users and their passwords
		self.admin_keys={}
		self.nonce = {}

		self.pipe.send(self.fileid_filename_secret_nonce_length)
		self.pipe.send(self.filename_admin)
		self.pipe.send(self.filename_listofusers)
		self.pipe.send(self.occupied)
		self.cip = ChaCha20Poly1305(hashlib.sha256(self.secret).digest())

		key = RSA.generate(2048)
		binprivkey = key.exportKey('DER')
		privk = RSA.importKey(binprivkey)
		self.privkey = privk
		a = 1<<41824
		with open(self.occupied,'w') as f:
			nonce = self.pipe.recv()
			self.pipe.send(self.cip.encrypt(nonce),bytearray(nonce))
			csvr = csv.writer(f)
			for i in range(10737):
				csvr.writerow(['0',a])

	def on_connect(self, connection):
		# for connection during file upload
		pass
	def on_disconnect(self, connection):
		pass

	def exposed_authenticat(self,userid, password):
		c = rpyc.connect('localhost',15892)	# in place of localhost, place the address of the location where 'server.py' program is running
		r = c.root.authenticat(userid, password)
		# check how to close the connection
		if r == 'authenticated' :
			self.authenticated.append(userid)
			self.authenticated_users[userid] = hashlib.sha256(str(password)).digest()
			# note that password itself is a hash
		return r

	def exposed_logout(self,userid,password):
		c = rpyc.connect('localhost',15892)
		r = c.root.logout(userid,password)
		# check how to close the connection
		if r == 'logout':
			self.authenticated.remove(userid)
			self.authenticated_users.pop(userid)
		return r
	def exposed_file_admin_request(self,admin_id,password, keyy):
		# send the nonce to be used while file upload
		password = hashlib.sha256(str(password)).digest()
		if self.authenticated_users[admin_id]!=password:
			return 'wrong password'
		d2 = pyDH.DiffieHellman()
		key = d2.gen_public_key()
		try:
			shared_key = d2.gen_shared_key(keyy)
		except:
			return 'use appropriate keys'
		nonce = os.urandom(12)
		self.admin_keys[admin_id] = shared_key

		self.nonce[admin_id] = nonce
		return [nonce,key]

	def exposed_admin_add_user(self,admin_id, password, userid, filename):
		# verify if the admin is logged in
		p = hashlib.sha256(str(password)).digest()
		if self.authenticated_users[admin_id] != password:
			return "login_again"
		# check if filename exists
		a = False
		with open(self.filename_admin,'r') as f:
			nonce = self.pipe.recv()
			self.pipe.send(self.cip.encrypt(nonce),bytearray(nonce))

			r = csv.reader(f,delimiter=",")
			d1 = list(r)
		with open(self.filename_listofusers,'r') as f:
			nonce  = self.pipe.recv()
			self.pipe.send(self.cip.encrypt(nonce),bytearray(nonce))
			rr = csv.reader(f,delimiter=",")
			dd = list(rr)

		for row in d1:
			if row[0] == filename and row[1] != hashlib.sha256(admin_id).digest():
				return 'not allowed'
		for ro in dd:
			if ro[0] == filename:
				ro.append(userid)
				a = True
				break
		if a == False:
			return 0
		with open(self.filename_listofusers,'w') as f:
			nonce = self.pipe.recv()
			self.pipe.send(self.cip)
			H = csv.writer(f)
			H.writerows(dd)

		return 0
	def exposed_file_access(self, userid, password, filename, client_key):
		# check if the user is logged
		p = hashlib.sha256(password).digest()
		if self.authenticated_users[admin_id] != password:
			return 'login_again'

		# check if the user is allowed to access the files
		a = False
		with open(self.filename_listofusers,'r') as f:
			nonce = self.pipe.recv()
			self.pipe.send(self.cip.encrypt(nonce),bytearray(nonce))

			r = csv.reader(f,delimiter=",")
			d = list(r)
			for ro in d:
				if ro[0] == filename:
					for e in ro:
						if e==userid:
							a = True

		if not a :
			return 'not allowed'
		with open(self.fileid_filename_secret_nonce_length,'r') as f :
			nonce = self.pipe.recv()
			self.pipe.send(self.cip.encrypt(nonce),bytearray(nonce))

			r = list(csv.reader(f,delimiter=","))
			for rr in r:
				if rr[1] == filename:
					filid = rr[0]
					secr = rr[2]
					nonc = rr[3]
					n = rr[4]

		l = []
		for i in range(n):
			v = self.privkey.encrypt(long(filid),'x')[0] % pow(32,6) + 1
			l.append(v)
			filid = v

		f = ""
		cip = ChaCha20Poly1305(hashlib.sha256(secret).digest())

		for a in range(n):
			value = list[a]
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
			path = self.base_path+"/"+path
					#print path+'file'
			try:
				with open(path+"file", "rb") as fil:
					nonce = self.pipe.recv()
					self.pipe.send(self.cip.encrypt(nonce),bytearray(nonce))
					f = f + str(cip.decrypt(nonc,fil.read()))

			except:
				return "error"

		d = pyDH.DiffieHellman()
		keyy= d.gen_public_key()
		shared_key = d.gen_shared_key(client_key)
		cip = ChaCha20Poly1305(hashlib.sha256(shared_key).digest())
		nonce = os.urandom(12)

		return [keyy,cip.encrypt(nonce,bytearray(f)),nonce]

	def exposed_remove_user(self,admin_id,password, userid):
		if self.authenticated_users[admin_id] != hashlib.sha256(password).digest():
			return 'login_again'
		with open(self.filename_admin,'r') as f:
			nonce = self.pipe.recv()
			self.pipe.send(self.cip.encrypt(nonce),bytearray(nonce))

			r = csv.reader(f,delimiter=",")
			d = list(r)
			for row in d:
				if row[0] == filename and row[1] != hashlib.sha256(admin_id).digest():
					return 'not allowed'
		with open(self.filename_listofusers,'r') as file:
			nonce = self.pipe.recv()
			self.pipe.send(self.cip.encrypt(nonce),bytearray(nonce))

			r = csv.reader(file,delimiter=",")
			d = list(r)

		for row in d:
			if row[0] == filename:
				for r in row:
					if r == userid:
						row.remove(r)
						break

		with open(self.filename_listofusers,'w') as file:
			nonce = self.pipe.recv()
			self.pipe.send(self.cip.encrypt(nonce),bytearray(nonce))

			w = csv.writer(file)
			w.writerows(d)

		return 0

	def exposed_file_upload(self,admin_id, file , password,filename, update = 0, *args):
		# password for preventing the attacks
		password = hashlib.sha256(str(password)).digest()
		if self.authenticated_users[admin_id] != password:
			return 'wrong password, operation not allowed'
		fileid = random.SystemRandom().randint(0,pow(32,7))
		cip = ChaCha20Poly1305(hashlib.sha256(self.admin_keys[admin_id]).digest())
		n = len(file)/127
		fileid = random.SystemRandom().randint(1,pow(32,6)-2)
		list = []
		c = 0
		f = open(self.occupied,'r')
		nonce = self.pipe.recv()
		self.pipe.send(self.cip.encrypt(nonce,bytearray(nonce)))
		r = csv.reader(f,delimiter = ",")
		d = list(r)
		f.close()

		while c<n:
			v = self.privkey.encrypt(long(fileid),'x')[0] % pow(32,6)+1
			r = v/41824
			x = v % 41824
			if d[r][1] & (1<<x) != 0:
				list = []
				fileid = random.SystemRandom().randint(1,pow(32,6)-2)
				c = 0
				continue
			list.append(v)
			fileid = v
		for a in list:
			row = a/41824
			x = a % 41824
			if x == 0:
				d[row][0] = '1'
			else:
				d[row][1] = d[row][1] | (1<<x)
		for a in range(n):
			value = list[a]
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

			base_path = self.base_path
			path = base_path+"/"+path
			#print path+'file'
			with open(path+"file", "wb") as fil:
				nonce_ = self.pipe.recv()
				self.pipe.send(self.cip.encrypt(nonce_,bytearray(nonce_)))
				try:
					fil.write(filee[a*127:a*127+127])
				except:
					return "error"

			# update the csv files.
			# update filename_admin
		try:

			with open(self.filename_admin,'w') as f:
				nonce = self.pipe.recv()
				self.pipe.send(self.cip.encrypt(nonce,bytearray(nonce)))
				w = csv.writer(f)
				w.writerow([filename,hashlib.sha256(admin_id).digest()])
			with open(self.filename_listofusers,'w') as f:
				nonce = self.pipe.recv()
				self.pipe.send(self.cip.encrypt(nonce,bytearray(nonce)))
				w = csv.writer(f)
				w.writerow([filename, hashlib.sha256(admin_id).digest()])
			with open(self.fileid_filename_secret_nonce_length,'w') as f:
				nonce = self.pipe.recv()
				self.pipe.send(self.cip.encrypt(nonce,bytearray(nonce)))
				w = csv.writer(f)
				w.writerow([fileid,filename,self.admin_keys[admin_id],self.nonce[admin_id]])
			with open(self.occupied,'w') as f:
				nonce = self.pipe.recv()
				self.pipe.send(self.cip.encrypt(nonce,bytearray(nonce)))
				w = csv.writer(f)
				w.writerows(d)

		except:

			with open(self.filename_admin,'r') as f_r:
				nonce = self.pipe.recv()
				self.pipe.send(self.cip.encrypt(nonce,bytearray(nonce)))
				r = csv.reader(f_r, delimiter=",")
				d1 = list(r)
				for row in d1:
					if row[0] == filename:
						d1.remove(row)
						break

			with open(self.filename_admin,'w') as f_w:
				nonce = self.pipe.recv()
				self.pipe.send(self.cip.encrypt(nonce,bytearray(nonce)))
				w = csv.writer(f_w)
				w.writerows(d1)

			with open(self.filename_listofusers,'r') as f_r:
				nonce = self.pipe.recv()
				self.pipe.send(self.cip.encrypt(nonce,bytearray(nonce)))

				r = csv.reader(f_r, delimiter=",")

				d = list(r)
				for row in d:
					if row[0] == filename:
						d.remove(row)
						break
			with open(self.filename_listofusers,'w') as f_w:
				nonce = self.pipe.recv()
				self.pipe.send(self.cip.encrypt(nonce,bytearray(nonce)))
				w = csv.writer(f_w)
				w.writerows(d)
			with open(self.fileid_filename_secret_nonce_length,'r') as f_r:
				nonce = self.pipe.recv()
				self.pipe.send(self.cip.encrypt(nonce,bytearray(nonce)))

				r = csv.reader(f_r, delimiter=",")
				d = list(r)
				for row in d:
					if row[0] == filename:
						d.remove(row)
						break
			with open(self.fileid_filename_secret_nonce_length,'w') as f_w:
				nonce = self.pipe.recv()
				self.pipe.send(self.cip.encrypt(nonce,bytearray(nonce)))
				w = csv.writer(f_w)
				w.writerows(d)

			return 'error'
		return "okay"

def exposed_file_delete(self, admin_id,filename, password):
		# authenticated
		p = hashlib.sha256(str(password)).digest()
		if self.authenticated_users[admin_id] != password:
			return 'login_again'

		with open(self.filename_admin,'r') as f:
			nonce = self.pipe.recv()
			self.pipe.send(self.cip.encrypt(nonce,bytearray(nonce)))
			d1 = list(csv.reader(f,delimiter=","))

		with open(self.fileid_filename_secret_nonce_length,'r') as f:
			nonce = self.pipe.recv()
			self.pipe.send(self.cip.encrypt(nonce,bytearray(nonce)))
			dd = list(csv.reader(f,delimiter=","))
		with open(self.filename_listofusers,'r') as f:
			nonce = self.pipe.recv()
			self.pipe.send(self.cip.encrypt(nonce,bytearray(nonce)))
			d3 = list(csv.reader(f,delimiter=","))
		with open(self.occupied,'r') as f:
			nonce = self.pipe.recv()
			self.pipe.send(self.cip.encrypt(nonce,bytearray(nonce)))
			d4 = list(csv.reader(f,delimiter=","))

		for x in d1:
			if x[0] == filename:
				d1.remove(x)
		for x in dd:
			if x[1] == filename:
				fileid = x[0]
				n = x[4]
				dd.remove(x)
		for x in d3:
			if x[0] == filename:
				d3.remove(x)
		try:
			with open(self.filename_admin,'w') as f:
				nonce = self.pipe.recv()
				self.pipe.send(self.cip.encrypt(nonce,bytearray(nonce)))
				w = csv.writer(f)
				w.writerows(d1)
			with open(self.fileid_filename_secret_nonce_length,'w') as f:
				nonce = self.pipe.recv()
				self.pipe.send(self.cip.encrypt(nonce,bytearray(nonce)))
				ww = csv.writer(f)
				ww.writerows(dd)
			with open(self.filename_listofusers,'w') as f:
				nonce = self.pipe.recv()
				self.pipe.send(self.cip.encrypt(nonce,bytearray(nonce)))
				www = csv.writer(f)
				www.writerows(d3)
		except:
			return 'error'
			# generate the list of nodes for this fileid
		for i in range(n):
			v = self.privkey.encrypt(long(fileid),'x')[0] % pow(32,6) + 1
			fileid = v
			row = v/41824
			x = v % 41824
			if x == 0:
				d4[row][0] = '0'
			else:
				d4[row][1] = d4[row][1] & (1<<(x+1))

		with open(self.occupied,'w') as f:
			nonce = self.pipe.recv()
			self.pipe.send(self.cip.encrypt(nonce,bytearray(nonce)))
			wwww = csv.writer(f)
			try:
				wwww.writerows(d4)
			except:
				return 'error'

		return 'deleted'

class DH:

    def __init__(self, unprivilegedProcessPipeEnd):
        self._unprivilegedProcessPipeEnd = unprivilegedProcessPipeEnd

    def share_key(self,root):
        invokerUid = os.getuid()

        d2 = pyDH.DiffieHellman()
        d2_key = d2.gen_public_key()
        self._unprivilegedProcessPipeEnd.send(d2_key)
        d1_key = self._unprivilegedProcessPipeEnd.recv()
        shared_key = d2.gen_shared_key(d1_key)

	g = GroupService(self._unprivilegedProcessPipeEnd, shared_key,root)
	from rpyc.utils.server import ThreadedServer
	t = ThreadedServer(g, port = 50001)
	t.start()
