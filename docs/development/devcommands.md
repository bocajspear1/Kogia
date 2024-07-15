# Development Commands

## `dev`

### `dev dbclean`

Cleans the database and truncates all collections. 

> Remember this clears out the database authentication too, so be sure to recreate your users.

### `dev insertdata`

Manually insert data into the database.

### `dev plugin PLUGIN_NAME JOB_UUID`

Run the plugin `PLUGIN_NAME` on the job with the UUID `JOB_UUID`.