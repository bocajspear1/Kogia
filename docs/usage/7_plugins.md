# Plugins

Plugins are at the core of Kogia's capabilities. All analysis is performed by plugins. Plugins are run in Jobs, and have ways to a few ways to configure how they operate.

## Plugin Info

To view plugin information, in the info dropdown in the top right, select "Plugins." This will show a list of currently enabled plugins organized by type of plugin. Selecting a plugin from the list shows any documentation provided and a list of arguments.

## Config

A plugin's configuration is its global settings, used for things like API keys and URLs. This is stored in the same directory as the plugin's main Python file as `config.json`. 