# Installation

For the core framework, install the following dependencies:

- **\>=Python3.8** (for backend), install necessary packages for a `venv`
- **NodeJS** (for frontend)
- **ArangoDB** (A Docker container works fine)

## Set up the Database

For local installs of ArangoDB, you can run the script `./scripts/create_arango_db.sh`, type in the ArangoDB root password created at installation, and a user will be automatically created with a random password. This password will be printed to standard out.

If not, you will manually need to create a user for Kogia to connect to (recommended), create a database, and grant that user full access to that database.

## Python and NodeJS Dependencies

- Clone in Kogia repo
- Create `venv` in repo directory, then activate:
```
python3 -m venv ./venv
source ./venv/bin/activate
```
- Install backend dependencies
```
pip3 install -r requirements.txt
```
- Install frontend dependencies:
```
cd frontend && npm install
```

## Configuration File

The example configuration file `config.example.json` is a good starting point. Copy it to `config.json`

```
cp config.example.json config.json
```

Then update `config.json` with details on the database and other modifications you'd like to make. View details on the configuration file [here](../administration/config.md).

## Building Containers

Before running the server, you will need to create the containers for various plugins. Run from the root of the repository. Simply run:

```
./kogiacmd container build
```

## First Run

You will need **2** terminals, one to run the backend server and one to run the development web server (using Vite.js)

First add a user for the local database authentication. Run from the root of the repository.
```
./kogiacmd dbauth adduser admin -r admin
```

You will be prompted for a password.

In terminal 1, run the backend server. Run from the root of the repository.
```
./kogiacmd run web
```

In terminal 2 run the development web server. Run in the `./frontend` directory.
```
npm run dev
```

To expose the development web server to the network, run as follows:
```
npm run dev -- --host 0.0.0.0
```