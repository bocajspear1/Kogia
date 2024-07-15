# Commands

Kogia comes with the CLI helper `./kogiacmd`, which provides a wide variety of functionality to managing your Kogia instance.

## container

### `container build`

If the containers for installed plugins are not built, build those Docker containers.

### `container check`

Checks if the container for container-based plugins are built and returns the result for each container-based plugin.

### `container rebuild <PLUGIN>`

Force rebuild the container for plugin `<PLUGIN>`. Plugins must be referenced by class name.

## run

### `run web`

Runs web interface and, unless disabled, workers as well.

#### Options

- **--noworkers**: Don't run workers
- **--port**/**-p** : Port to bind to
- **--address**/**-a** : Address to listen on
- **--waitress**: Run web server with the waitress library instead of default gunicorn.

### `run workers`

Run only workers without the web interface, For distributed setups.
