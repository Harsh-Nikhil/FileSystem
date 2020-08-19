# A File repository system for storing classified information
(This was a term project for 'Theory and practice of computer systems security' course at IISc Bangalore during Autumn 2019).    

This is the implementation of a new proposal to store classified information on untrusted servers. The proposal ensures security of information even in case the attacker has physical access to the storage hardware. The proposed system reduces the probabilty of a successful attack to less than 2^{-20000}.  

Please see [here](/Readme_implementation_details.pdf) for the complete proposal.
 
This implementation will run in python version(2.7).

# Usage:
<code>python 'f system.py' root_folder mnt_folder host </code>  
For running on the local machine, replace host by 'localhost'  
The default port for SingleUserService is port = 15892. The default port for GroupService is port = 50001  
If you are a server admin, configure the 'host' accordingly.

# Dependencies:
* hashlib
* pymongo
* chacha20poly1305
* pycryptodome (Crypto)
* pyDH
