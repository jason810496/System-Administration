# Writeup
Tips : 
1. finish `health` api
2. check `localhost` 
3. finish `rc.d` and add your service
4. finish `nginx` and `ssl`
5. finish the rest of `api`

## Prerequisite
- wireguard connection 
    - `wg-quick up judge`
## General
- install `poetry`
```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="/home/{USERNAME}/.local/bin:$PATH"
```

[install poetry with the official installer](https://python-poetry.org/docs/#installing-with-the-official-installer)

- Create a FreeBSD service named `hw4`. Provide service `hw4 [start |restart | stop]` commands to control your service.

```bash
sudo curl url -o /usr/local/etc/rc.d/hw4
```

the service script could be reference from `/usr/local/etc/rc.d/wireguard` wireguard service setting . 