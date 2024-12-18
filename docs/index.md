# Home

Kogia is a modular, plugin-based **malware analysis framework**. The Kogia framework brings together sample storage and a wide variety of analysis capabilities into one application using a plugin-based design, flexible data structure, and configurable web interface.

## Malware Analysis

Kogia is built to analyze submitted software to determine if it is malware (malicious software) or not. Using a wide variety of tools and proper plugins, Kogia can perform *static* (the sample is not executed) and *dynamic* (the sample is executed and monitored) analysis on any file you'd want.

## Modular

Kogia is built around plugins, plugins for analysis, plugins for storage, plugins for authentication. This ensures Kogia can be made to fit your workflows, whether small-scale or mass sample submissions.

The most critical plugin are analysis plugins. Almost all analysis is done with analysis plugins which utilize common tools you're familiar with, like Detect-It-Easy, CAPA, YARA and more. Kogia brings these tools all together allowing you to view and break down the output from each in one convenient location. Got a favorite tool not already integrated or a new exciting tool you want to put into your analysis pipeline? Analysis plugins allow you to add them easily in a script or container.

## Flexible Data Structure

Kogia is built on a flexible data structure that plugins can utilize to simpify your analysis's data. Inserting data into this data structure also allows exploring interconectivity between malware indicators through Kogia's use of a graph database.

## Powerful Web Interface and API

Kogia provides a powerful web UI that allows you to easily upload samples and view the results from your analysis. No need to build custom plugin configuration panels, Kogia automatically takes plugin parameters and builds the UI to present them to users. If you're looking for more automated submissions, Kogia provides a powerful API (which the UI actually uses) to submit, run jobs, and extract data.

## Get Going with Kogia

- [Getting Started](getting-started.md)
- [Installation](installation.md)
- [Usage Guide](usage/1_uploading.md)

