# Writeup
Tips : 
1. finish `health` api
2. check `localhost` 
3. finish `rc.d` and add your service
4. finish `nginx` and `ssl`
5. finish the rest of `api`

## Prerequisite
- Wireguard connection 
    - `wg-quick up judge`
- Create a directory under `/var` named `raid` to simulate disks.
    - `sudo mkdir /var/raid/`

## General
### setup web application environment : 
> choose either 1. or 2.
> ( I faced this [issue](https://github.com/PyO3/maturin/issues/607) using first method )
> 
> Since `venv` could also manage pip , so I use second method .
1. use `poetry` as pip manager : 
    - clone web application template
    - install `poetry`
    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="/home/{USERNAME}/.local/bin:$PATH"
    ```

    [install poetry with the official installer](https://python-poetry.org/docs/#installing-with-the-official-installer)

    - install newer python3 version ( the 3.9 version will encounter bugs ) : 
    ```bash
    sudo pkg install python310
    poetry env use python3.10
    ```
    - initialize environment :

2. use `venv` as virtual environment:
    - clone web application template
    - setup `venv` and install requirements 
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip3 install python-dotenv fastapi uvicorn loguru python-multipart pytest pytest-asyncio requests httpx
    ``` 
    Note that : 
        - `source venv/bin/activate` will enter python virtual environment
        - `deactivate` will quit python virtual environment
    - start app command
    ```
    cd api && python3 -m uvicorn app:APP --reload --host 0.0.0.0
    ```

### Create a FreeBSD service named `hw4`. Provide service `hw4 [start |restart | stop]` commands to control your service.

- copy service script and add permission : 
```bash
sudo curl https://raw.githubusercontent.com/jason810496/System-Administration/main/hw4/hw4 -o /usr/local/etc/rc.d/hw4
sudo chmod +x /usr/local/etc/rc.d/hw4
```
- usage of service : 
    - start service
    ```bash
    sudo service hw4 start
    ```
    - stop service
    ```bash
    sudo service hw4 stop
    ```
    - restart service ( restart = stop + start )
    ```bash
    sudo service hw4 restart
    ```

- check process : 
```bash
sudo ps u
```
- if the web app started successfully ( the process related with `python` are all web app ):
    ```
    USER    PID %CPU %MEM   VSZ   RSS TT  STAT STARTED    TIME COMMAND
    root 12015  1.8  1.6 42652 32132  2  S    06:46   0:00.15 /usr/home/Jason/System-Administration/hw4/app/venv/bin/python3 -c from multiprocess
    root 12013  1.0  1.1 35980 23328  2  S    06:46   0:00.15 python3 -m uvicorn app:APP --reload --host 0.0.0.0 (python3.9)
    root 12014  0.7  0.6 23440 12152  2  S    06:46   0:00.02 /usr/home/Jason/System-Administration/hw4/app/venv/bin/python3 -c from multiprocess
    root  1501  0.0  0.2 14592  4676  1  Is+  04:09   0:00.39 -bash (bash)
    root 11420  0.0  0.2 14592  4452  2  Ss   05:51   0:00.16 -bash (bash)
    root 12016  0.0  0.1 13464  2888  2  R+   06:46   0:00.00 ps u
    ```
- after stop web app : 
    ```
    USER    PID %CPU %MEM   VSZ  RSS TT  STAT STARTED    TIME COMMAND
    root  1501  0.0  0.2 14592 4676  1  Is+  04:09   0:00.39 -bash (bash)
    root 11420  0.0  0.2 14592 4452  2  Ss   05:51   0:00.17 -bash (bash)
    root 12034  0.0  0.1 13464 2884  2  R+   06:47   0:00.00 ps u
    ```

- Notes : 
    - the service script could be reference from `/usr/local/etc/rc.d/wireguard` wireguard service setting .
    - the `stop` function `kill` all `pid` related to web app . 

### Certification
- Download `sacertbot` from judge server and use the `sacertbot` to download your CA certificate and CA key.
    ```bash
    scp ~/Downloads/sacertbot.txt FreeBSD:~/sacertbot.sh
    sudo pkg install wget zip
    chmod +x sacertbot.sh
    ./sacertbot.sh
    ```
- unzip `ca.zip` in after runing `sacertbot.sh` 
    ```
    uzip ca.zip
    ls # `ca.crt` `ca.key` should be in current directory
    ```
<!-- - Generate a private key and CSR for the web certificate:
```
openssl req -new -newkey rsa:2048 -nodes -keyout web.key -out web.csr
```
The command is interative , replace `STUDENT_ID` with your own student id .
```
writing new private key to 'web.key'
-----
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:TW
State or Province Name (full name) [Some-State]:
Locality Name (eg, city) []:
Organization Name (eg, company) [Internet Widgits Pty Ltd]:
Organizational Unit Name (eg, section) []:
Common Name (e.g. server FQDN or YOUR name) []:STUDENT_ID
Email Address []:

Please enter the following 'extra' attributes
to be sent with your certificate request
A challenge password []:
An optional company name []:
``` -->
<!-- - Create a configuration file (e.g., `openssl.cnf`) with the following content:
    - Replace `STUDENT_ID` with the common name you want for your web certificate ( `student_id` ), and `example.com` with your domain name ( `xxx.sa` ).
```
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
CN = STUDENT_ID

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = jasonbigcow.sa
```
- Generate a certificate request:
```
openssl req -new -key ca.key -out web.req
```
- Sign the web certificate using the CA certificate and private key:
```
openssl x509 -req -days 365 -sha256 -extfile openssl.cnf -signkey ca.key -in web.req -out web.crt
```
- Sign root CA:
```
openssl x509 -req -days 365 -sha256 -extfile openssl.cnf -signkey ca.key -in web.req -out web.crt
``` -->

<!-- - Sign the web certificate using the CA certificate and private key:
```
openssl x509 -req -in web.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out web.crt -days 365 -extensions v3_req -extfile openssl.cnf
```
The result of signing certificate : 
```
Signature ok
subject=C = TW, ST = Some-State, O = Internet Widgits Pty Ltd, CN = F74116720
Getting CA Private Key
``` -->

- Generate our own certificate.
```
openssl req -new -newkey rsa:2048 -nodes -keyout web.key -out web.csr
```
- Concatenate the certificate chain files:
```
cat web.crt ca.crt rootca.crt > web_chained.crt
```
- Sign the certificate chain using the root CA and intermediate CA:
```
openssl ca -config openssl.cnf -in web_chained.crt -cert ca.crt -keyfile ca.key -out web_chained_signed.crt
```
- Now we can use `web_chained_signed.crt` and `web.key`

### Nginx Configuration
- Install `nginx` package using pkg.
    - `sudo pkg install ngnix`
- `Nginx` Configuration
    - edit `rc.conf`:
    ```bash
    sudo vim /etc/rc.conf # and add the following line 
    nginx_enable="YES"
    ```
    - copy configuration file : 
    ```bash
    curl URL -o /usr/local/etc/nginx/nginx.conf
    nginx -t # check config file syntax
    ```
    - edit web certification : 
        - replace `/path/to/USERNAME.crt` to the certificate just signed
        eg : `/home/aaa/aaa.web.crt`
        ```
        sudo vim /usr/local/etc/nginx/nginx.conf
        ```
    - restart nginx
    ```
    sudo service nginx restart
    ```
- Test `Nginx` Configuration
    - http
    - `curl username.sa`


## Web interface


