import hashlib
userid = ""
import csv

def authenticate(userid, password):
    import rpyc
    c = rpyc.connect('localhost', 15892)
    om = c.root.authenticat(userid,password)
    return om

def register():
    ussername = input("Enter your username:")
    password = input("Enter your password:")
    password = hashlib.sha256(password).digest()
    import rpyc
    c = rpyc.client('localhost',15892) # localhost can be modified alognwith the port # ID
    userid = c.root.register_user(ussername,password)
    # save this userid in localfile
    with open('.wrapCloud/userid/local/userid','w') as f:
        f.write(userid)
    from Crypto
    import Crypto.PublicKey import RSA
    key = RSA.generate(2048)
    binPrivKey = key.exportKey('DER')
    binPubKey = key.publickey().exportKey('DER')
    with open('.wrapCloud/userid/local/pub','wb') as f:
        f.write(binPubKey)
    with open('.wrapCloud/userid/local/pri','wb') as f:
        f.write(binPrivKey)
    c.close()

    print 'register'

def upload_file():
    path = raw_input('Enter file path : ')
    with open(path,'r') as f:
        file = f.read()
    with open('.wrapCloud/userid/local/pub','rb') as f, open('.wrapCloud/userid/local/userid','r') as f2:
        pubKeyObj = RSA.importKey(f.read())
        userid = f2.read()

    file = pubKeyObj.encrypt(file,'x')[0]
    import rpyc
    c = rpyc.client('localhost',15892)
    password = hashlib.sha256(input('Enter your password: ').digest())
    authenticate(userid,password)
    # calculate the fileid and filesequence. Also, need to maintain the occupied list.
    n = len(file)/127
    ifileid = random.SystemRandom().randint(1, pow(32,5)-1)
	fileseqs = []
	# now starts the file sequences
	for i in range(n):
		fileid = pubKeyObj.encrypt(ifileid)%(pow(32,5)-1)+1
		fileseqs.append(fileid)
        ifileid = fileid

    r = c.root.exposed_file_upload_user(userid,file,fileseqs)
    if r=='okay':
        with open('.wrapCloud/userid/local/fileid.csv','w') as f:
            w = csv.writer(f)
            w.writerow([path,ifileid,n])

    return r

def logout(userid,password):
    import rpyc
    c = rpyc.connect('localhost',15892)
    return c.root.logout(userid,password)

def delete_file():
    path = raw_input("Enter file path: ")
    # clear the nodel lis
    with open('.wrapCloud/userid/local/userid','rb') as f:
        userid = f.read()
    with open('.wrapCloud/userid/local/fileid.csv','r') as f:
        r = csv.reader(f)
        d = list(r)
    for r in d:
        if r[0] == path:
            fileid = r[1]
            n = r[2]
            break
    with open('.wrapCloud/userid/local/pub','rb') as f:
        pubKeyObj = RSA.importKey(f)

    fileseqs = []
	# now starts the file sequences
	for i in range(n):
		fileid = binPubKey.encrypt(fileid)%(pow(32,5)-1)+1
		fileseqs.append(fileid)
    import rpyc
    c = rpyc.connect('localhost',15892)
    r = c.root.file_delete_user(userid,fileseqs)
    if r=='authentication_failed':
        password = hashlib.sha256(input('Enter your password : ').digest())
    r = c.root.authenticat(userid,password)
    if r=='authenticated':
        r = c.root.file_delete_user(userid, fileseqs)
    #TODO: implement the nodelist part for client. For GroupService, it is already impemented
    return r
