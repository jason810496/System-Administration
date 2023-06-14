# Writeup
Tips : 
1. finish `health` api
2. check `localhost` 
3. finish `rc.d` and add your service
4. finish `nginx` and `ssl`
5. finish the rest of `api`

My tools : 
- `rsync` : remote sync 
    ```
    rsync -r hw4 FreeBSD:/home/Jason/System-Administration/ --exclude=venv
    ```
- `syncToFreeBSD.sh` : 
    - prerequisite : `brew install watch`
    - auto sync `hw4` directory while deveplopment folder change !

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
- Download `sacertbot` from judge yourwebcrt and use the `sacertbot` to download your CA certificate and CA key.
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
- Create our own CSR (Certificate Signing Request) and specifies the subject of the certificate to be included in the CSR : 
    ```bash
    openssl req -new -key ca.key -out yourwebcrt.csr -subj "/C=TW/ST=TW/L=TAINAN/O=NCKU/CN=jasonisbigcow.sa" -addext "subjectAltName=DNS:jasonisbigcow.sa"
    ```
Options used:
- `-new`: Generates a new CSR.
- `-key ca.key`: Specifies the private key file (`ca.key`) to be used for generating the CSR.
- `-out yourwebcrt.csr`: Specifies the output file (yourwebcrt.csr) where the generated CSR will be saved.
- `/C`: Country (TW for Taiwan in this case)
- `/ST`: State (TW for Taiwan in this case)
- `/L`: Location or city (TAINAN in this case)
- `/O`: Organization (NCKU in this case)
- `/CN`: Common Name (`jasonisbigcow.sa` in this case)

Create an `openssl.conf` configuration file .
```
[req] req_extensions = v3_req
 distinguished_name = req_distinguished_name
 [req_distinguished_name]
countryName = TW
 stateOrProvinceName = TW
 localityName = TAINAN
 organizationName = NCKU
 commonName = jasonisbigcow.sa
 [v3_req] 
 subjectAltName = DNS:jasonisbigcow.sa
```

Sign Certificate Signing Request (CSR) and generate a certificate.
```
openssl x509 -req -in yourwebcrt.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out yourwebcrt.crt -days 365 -extfile openssl.cnf -extensions v3_req
```

Chained our certificate with `ca.crt`
```
cat yourwebcrt.crt ca.crt > chained.crt
```

Update `Nginx` configuration : located at `/usr/local/etc/nginx/nginx.conf` :
```bash
#....
    ssl_certificate /home/Jason/chained.crt;                                
    ssl_certificate_key /home/Jason/ca.key;
#....
```


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
    - `curl https://jasonisbigcow.sa/api/health --insecure`
    - `curl username.sa`
    ```
    python3 -c "import requests;print(requests.get('https://jasonisbigcow.sa').text)" echo | openssl s_client -connect jasonisbigcow.sa:443 2>&1 1>/dev/null
    ```

## Web interface
- `api/health`
in `app/api/endpoints/health.py` line 17 , replace `"/"` to `""`
```python
@router.get(
    "/",   # <--- here
    status_code=status.HTTP_200_OK,
    responses=GET_HEALTH,
    response_model=schemas.Msg,
    name="health:get_health",
)
```

- create raid : 
check command : 
```
xxd /var/raid/block-0/m3ow.txt
xxd /var/raid/block-1/m3ow.txt
xxd /var/raid/block-2/m3ow.txt
xxd /var/raid/block-4/m3ow.txt
```


