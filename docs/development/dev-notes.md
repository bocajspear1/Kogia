# Development Notes

## Structure

The general structure of the codebase is as follows:

- `backend`: Contains all backend code which serves up the API and does most of the work. This is written in Python 3 and Flask.
- `docs`: Contains all the documentation
- `frontend`: Contains all the frontend code written as a VueJS application using the [Bulma CSS](https://bulma.io/) framework.
- `plugins`: Contains all the plugins built-in to Kogia. Each plugin has a unique directory with its `plugin.py` file inside it.
- `tests`: Contains tests and test data.