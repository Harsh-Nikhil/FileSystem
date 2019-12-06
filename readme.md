This implementation will run in the python version (2.7).

The code base for WrapCloud.

# Usage:
<code>python 'f system.py' root_folder mnt_folder host </code>

In case for running on local machine, replace host by 'localhost'

The default port for SingleUserService is port = 15892. The default port for GroupService is port = 

If you are a server admin, configure the 'host' accordingly.

# Dependencies:
* hashlib
* pymongo
* chacha20poly1305
* pycryptodome (Crypto)
* pyDH
