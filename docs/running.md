# Running Kogia

Running and managing the Kogia backend server is done with `kogiacmd` script. See [here](./administration/commands.md) for more details.

## Dependency Services

- Ensure the database service is running (ArangoDB).
- Ensure any services your plugins depend on are running too.

## Preparing Plugin Containers

If haven't already, ensure the needed plugin containers are built with the `container build` command.

```shell
./kogiacmd container build
```

You can check to see if all the containers are built with the `container check` command:

```shell
$ ./kogiacmd container check
YARAPlugin: EXISTS
DetectItEasyPlugin: EXISTS
...
```

## Running the Backend

To run the backend manually, in the project's directory run:

```shell
./kogiacmd run web
```

This will start the backend server on port `4000`. This can be changed with `-p` argument.

## Frontend

### Production

The built VueJS application should be able to be served from any web server, including Kogia's backend server.

### Development

If you are running Kogia for development, you'll need to run the ViteJS development server by going into the `frontend` directory and running:

```
npm run dev
```

See the [install guide](./development/installation.md) for more details.