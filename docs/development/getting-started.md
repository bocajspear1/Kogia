# Development Getting Started

## Installation

See the [install guide](./installation.md).

## Developing Plugins

Plugins are stored in the `plugins` directory, and usually consist of a few files:

- `plugin.py`: The main Python file. It is required to have the top-level variable `__PLUGIN__` set to the Python class. (e.g. `__PLUGIN__ = CapaPlugin`). Plugin classes can import from different parent classes to enable different functionality. (`DockerPluginBase` for Docker container plugins, `HTTPPluginBase` for web-request-based plugins.)
- `plugin.json` (optional): JSON-formatted plugin configuration values. These values are loaded when the plugin is loaded.
- `options.json` (optional): Contains list of arguments for the plugin. These are automatically loaded and displayed in the web UI when creating new analysis jobs.
- `display.json` (optional): Contains list of actions and display items for viewing plugin data in the web UI under the Plugins page.
- `Dockerfile` (Container based plugins only): Dockerfile for the analysis container.

Testing plugins can be a bit tedious at times, especially container based ones. If your container has issues, be sure to rerun rebuild for the container:

```
./kogiacmd container rebuild <PLUGIN_CLASS>
```

To run a plugin on an existing job, you can use the `kogiacmd` script:

```
./kogiacmd dev <PLUGIN_CLASS> <JOB_UUID>
```

### Container Variables

Kogia mounts a read-only directory into the container and sets environment variables for the tool to use.

- `${TMPDIR}`: A temporary directory with a randomly generated name where the submission's files are mounted read-only into the container.
- `${SUBMITFILE}`: The name of the file being operated on.

## Developing the Backend

> Remember that all analysis functionality should be in plugins!

## Developing the Frontend