# K-Door-web

# Development setup

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

## Initialize database

    source venv/bin/activate
    curl http://172.21.43.1:5000/user > ad.json
    python3 -m kdoorweb initdb


## Run dev server

    source venv/bin/activate
    python -m kdoorweb

Or

    bottle.py --debug --reload kdoorweb:application

To set the TCP port number add it as the last argument

    python -m kdoorweb 8888


# Notification server

You need a nginx server with nchan module to send realtime events
to the kdoorpi part of the project

example nchan conf snippet

```
location ~ /notify/(\w+)$ {
    nchan_pubsub;
    nchan_channel_id $1;
    nchan_store_messages off;
}
location /notify_status {
    nchan_stub_status;
}
```

## Run unittests

    source venv/bin/activate
    python -m unittest discover tests

## Update requirements.txt

    source venv/bin/activate
    pip-compile --upgrade setup.py
    pip-compile --upgrade dev-requirements.in
    # Apply updates to current venv
    pip-sync dev-requirements.txt requirements.txt
