# Configuration File

The configuration for Kogia is `config.json`, usually located in the main Kogia directory. The format is in JSON. `config.example.json` contains a sample configuration.

This page goes over the main keys in the configuration.

- **certfile**: Path to the certificate to use for HTTPS
- **keyfile**: Path to the private key to use for HTTPS

> For testing and evaluation, a self-signed key can be generated with:

```
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/C=US/O=Kogia/OU=Kogia Malware Analysis/CN=localhost"
```

- **db**: Database configuration. Currently [ArangoDB](https://arangodb.com/) is supported.
    - **host**: Database host. For a container or locally hosted DB use `localhost`.
    - **port**: Port to connect to. For ArangoDB this should be by default `8529`.
    - **user**: User to connect to the DB with. An unprivileged user is normally recommended.
    - **password**: Password for DB user
    - **db_name**: Name of the database to use.
- **auth**: Type of authentication to use. Format must be object with value name of the authentication class to use, under which goes any configuration values. (See [Authentication](auth.md)). For example:
```
"auth": {
    "DBAuth": {}
},
```

- **filestore**: Type of filestore to use. Format must be object with value name of the filestore class to use, under which goes any configuration values. (See [Filestores](filestores.md)). For example:
```
"filestore": {
    "FileStoreFS": {
        "dir": "./someplace"
    }
},
```
- **worker**: Type of worker to use. Format must be object with value name of the worker class to use, under which goes any configuration values. (See [Workers](workers.md)). For example:
```
"worker": {
    "WorkerThread": {
        "max_file": 3
    }
},
```
- **default_zip_password**: Default password for encrypted ZIP files containing samples. A popular on is `infected`.
- **loglevel**: The level of logging. Can be `debug`, `info`, `warning`, `error`.
- **docs_dir**: Directory to look for documentation for in-app user guide display.