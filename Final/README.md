# SA Final 

<!-- 

username : jasonisbigcow
pass : SaIsBigCow0424

 -->
## my note 

[HW1](https://hackmd.io/P0R7bELwQjaQpdCxG-0WoQ)


ssh to judge
```
ssh jasonisbigcow@10.187.16.54
```

1. timezone : 
sudo ntpdate
clock.stdtime.gov.tw
```
vi /etc/login.conf
```
add
```
:timezone=UTC+8:\
```
restart
```
cap_mkdb /etc/login.conf
reboot
```

```
sudo ntpdate clock.stdtime.gov.tw
```

2. Update the hostname to <username>.

```
sudo hostname jasonisbigcow.sa
```

3. Generate a user account called judge that fulfills the specified criteria.
○ Set the user password to m30owme0w.
○ Configure the default shell to be Bash.
○ Enable password-less use of the sudo command for the user.
○ Ensure the user can login using the SSH keys we provided. You can
obtain the SSH key from https://sa.imslab.org/pubkey.

```
adduser
```

result

```
Username: judge
Full name: judge
Uid (Leave empty for default):
Login group [judge]:
Login group is judge. Invite judge into other groups? []:
Login class [default]:
Shell (sh csh tcsh bash rbash git-shell nologin) [sh]: bash
Home directory [/home/judge]:
Home directory permissions (Leave empty for default):
Use password-based authentication? [yes]:
Use an empty password? (yes/no) [no]:
Use a random password? (yes/no) [no]:
Enter password:
Enter password again:
Lock out the account after creation? [no]:
Username   : judge
Password   : *****
Full Name  : judge
Uid        : 1002
Class      :
Groups     : judge
Home       : /home/judge
Home Mode  :
Shell      : /usr/local/bin/bash
Locked     : no
OK? (yes/no): yes
adduser: INFO: Successfully added (judge) to the user database.
Add another user? (yes/no): no
Goodbye!
```

Enable password-less use of the sudo command for the "judge" user by adding an entry 
```
sudo visudo
```

Obtain the SSH public key for the "judge" user by downloading it from the provided URL: https://sa.imslab.org/pubkey. You can use the wget command to download the file:

```
wget https://sa.imslab.org/pubkey -O /tmp/judge.pub
sudo mkdir -p /home/judge/.ssh
sudo cp /tmp/judge.pub /home/judge/.ssh/authorized_keys
````

```
sudo chown -R judge:judge /home/judge/.ssh
sudo chmod 700 /home/judge/.ssh
sudo chmod 600 /home/judge/.ssh/authorized_keys
```


Me : 

setup our ssh config also






4. You are tasked with modifying the SSH configuration file(s) on your
machine to comply with the following rules.
○ Only allow user login with private keys, prohibiting password-based
authentication.
○ Restrict SSH access by disallowing root login.
○ Modify the SSH port to use port 2222.

```
sudo vim /etc/ssh/sshd_config
```

edit : 
```
PasswordAuthentication no
PermitRootLogin no
Port 2222
```

restart service 
```
service sshd restart
```



5. Fix ZFS

chk
```
sudo zpool import
```
result
```
   pool: sa_pool
     id: 13942551464834721071
  state: DEGRADED
status: One or more devices contains corrupted data.
 action: The pool can be imported despite missing or damaged devices.  The
	fault tolerance of the pool may be compromised if imported.
   see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-4J
 config:

	sa_pool                   DEGRADED
	  mirror-0                DEGRADED
	    11169224777599426243  UNAVAIL  invalid label
	    da2                   ONLINE
[Jason@jasonisbigcowfinal ~]$ sudo zpool import sa_pool
[Jason@jasonisbigcowfinal ~]$ sudo zpool status sa_pool
  pool: sa_pool
 state: DEGRADED
status: One or more devices could not be used because the label is missing or
	invalid.  Sufficient replicas exist for the pool to continue
	functioning in a degraded state.
action: Replace the device using 'zpool replace'.
   see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-4J
  scan: resilvered 1.52M in 00:00:01 with 0 errors on Sat Jun 10 10:08:06 2023
config:

	NAME                      STATE     READ WRITE CKSUM
	sa_pool                   DEGRADED     0     0     0
	  mirror-0                DEGRADED     0     0     0
	    11169224777599426243  UNAVAIL      0     0     0  was /dev/da1
	    da2                   ONLINE       0     0     0
```

Check the status of the pool to see if it's imported and the state of the devices:
```
zpool import sa_pool
```

chk 
```
sudo zpool status sa_pool
```

fix
```
sudo zpool replace sa_pool /dev/da1
```

chk 
```
sudo zpool status sa_pool
```

6. Web client 

```
sudo vim /etc/hosts
```

```
10.187.10.1  sa-judge.meow
```



Web Server


7. setup nginx server with load balancing

```
sudo pkg install nginx
```

```
sudo sysrc nginx_enable=YES
```

ca : 
downlaod to FreeBSD & start sign crt 

generate new
```
openssl req -new -key ca.key -out jason.csr -subj "/C=TW/ST=TW/L=TAINAN/O=NCKU/CN=jasonisbigcow.ncku" -addext "subjectAltName=DNS:jasonisbigcow.ncku"
```

openssl.cnf
```
[req] req_extensions = v3_req
 distinguished_name = req_distinguished_name
 [req_distinguished_name]
countryName = TW
 stateOrProvinceName = TW
 localityName = TAINAN
 organizationName = NCKU
 commonName = jasonisbigcow.ncku
 [v3_req] 
 subjectAltName = DNS:jasonisbigcow.ncku
```

sign
```
openssl x509 -req -in jason.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out jason.crt -days 365 -extfile openssl.cnf -extensions v3_req
```

chain
```
cat jason.crt ca.crt > chained.crt
```

nginx : 
```
sudo vim /usr/local/etc/nginx/nginx.conf
```

```
sudo service nginx restart
```

Malicious Processes:

check processs
```
ps aux
```
kill process
```
kill -9 pid
```


Firewall

enable
```
sudo sysrc pf_enable=YES
sudo sysrc pflog_enable="YES"
sudo sysrc pfsync_enable="YES"
```

```
sudo vim /etc/pf.conf
```


<!-- old -->
<!-- pf.conf
```
# Set default behavior to block all incoming and outgoing traffic
set block-policy drop

# Allow all loopback and outgoing traffic
pass out on egress
pass in on lo0

# Allow incoming traffic for ICMP, SSH, NFS, and Web
pass in on eth0 inet inet proto icmp all
pass in on eth0 inet inet proto tcp from any to any port ssh
pass in on eth0 inet inet proto {tcp, udp} from 10.187.0.0/23 to any port nfs
pass in on eth0 inet inet proto {tcp, udp} from 10.187.0.0/23 to any port http
pass in on eth0 inet inet proto {tcp, udp} from 10.187.0.0/23 to any port https

# Create a whitelist for SSH and NFS services
table <whitelist_ssh_nfs> { 10.187.0.0/23, 10.187.112.0/20 }
pass in on eth0 inet inet proto {tcp, udp} from <whitelist_ssh_nfs> to any port {ssh, nfs}

# Create a blacklist for Nginx services
table <blacklist_nginx> { 10.187.10.5, 10.187.0.253 }
block in on eth0 inet inet proto {tcp, udp} from <blacklist_nginx> to any port {http, https}

# Deny other IPs trying to connect to SSH and NFS services
block in on eth0 inet inet proto {tcp, udp} to any port {ssh, nf}s

# Reload the firewall rules
load anchor "pf/*"
``` -->


<!-- old -->
<!-- ```
# Set default behavior to block all incoming and outgoing traffic
#set block-policy drop

# Allow all loopback and outgoing traffic
pass out on eth0
pass in on lo0

# Allow incoming traffic for ICMP, SSH, NFS, and Web
pass in on eth0 inet proto icmp all
pass in on eth0 inet proto tcp from any to any port ssh
pass in on eth0 inet proto {tcp, udp} from 10.187.0.0/23 to any port nfs
pass in on eth0 inet proto {tcp, udp} from 10.187.0.0/23 to any port http
pass in on eth0 inet proto {tcp, udp} from 10.187.0.0/23 to any port https

# Create a whitelist for SSH and NFS services
table <whitelist_ssh_nfs> { 10.187.0.0/23, 10.187.112.0/20 }
pass in on eth0 inet proto {tcp, udp} from <whitelist_ssh_nfs> to any port {ssh, nfs}

# Create a blacklist for Nginx services
table <blacklist_nginx> { 10.187.10.5, 10.187.0.253 }
block in on eth0 inet proto {tcp, udp} from <blacklist_nginx> to any port {http, https}

# Deny other IPs trying to connect to SSH and NFS services
block in on eth0 inet proto {tcp, udp} to any port {ssh, nfs}

# Reload the firewall rules
#load anchor "pf/*"
``` -->

<!-- new -->
```
# Define IP ranges for SSH and NFS access
ssh_access = "{ 10.187.0.0/23, 10.187.112.0/20 }"
nfs_access = "10.187.0.0/23"

# Allow all loopback and outgoing traffic
set skip on lo0
pass out all

# Allow ICMP traffic
pass in quick on eth0 inet proto icmp

# Allow SSH traffic from specified IP ranges
pass in quick on eth0 inet proto tcp from $ssh_access to any port 2222

# Allow NFS traffic from specified IP range
pass in quick on eth0 inet proto tcp from $nfs_access to any port 2049

# Allow web traffic only from all IPs except blocked IPs
block in quick on eth0 inet from { 10.187.10.5, 10.187.0.253 } to any
pass in quick on eth0 inet proto tcp to eth0 inet port 80
```


temp : 
```
set skip on lo0

# Allow all incoming and outgoing traffic on the external interface
pass in all on eth0 inet
pass out all on eth0 inet
```


```
sudo pfctl -f /etc/pf.conf
sudo service pf restart
```


NFS 

[ref](https://www.twbsd.org/cht/book/ch21.htm)

enable nfs client
```
nfs_client_enable="YES"
```

```
nfsiod
```

```
showmount -e nfs.sa
```

mount : 
```
mkdir /nfs_mount
sudo mount -t nfs nfs.sa:/flagplace /nfs_mount
```

```
chmod +x genflag.sh
./genflag.sh jasonisbigcow
```

nfs server  :


rc.d
```
sudo sysrc rpcbind_enable="YES"
sudo sysrc nfs_server_enable="YES"
sudo sysrc mountd_enable="YES"
```

share point :
```
mkdir -p /data/shared
sudo chmod 755 /data/shared
sudo chown nobody:nogroup /data/shared
sudo cp /home/Jason/flag /data/shared
```

```
sudo touch /etc/exports
sudo vim /etc/exports
```

add the following 
```
/data/shared -alldirs -mapall=nobody -network 10.187.1.0 -mask 255.255.255.0
/data/shared -alldirs -ro -network 0.0.0.0 -mask 0.0.0.0
```


restart nfs server
```
service nfsd onestart
```





## Testing 
hostname
```
hostname
```

ssh outh only
```
sshpass -p m30owme0w ssh -o PubkeyAuthentication=no -o PreferredAuthentications=keyboar d-interactive,password -p 2222 judge@10.187.16.54 whoami
```

highest point : 74 

