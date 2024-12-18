# Getting Started

Welcome to Kogia! The Kogia framework is a highly modular and extensible malware analysis framework, built for easy integration of new tools and malware data analysis and exploration.

## Installation 

Kogia is built with Python 3, ArangoDB, and Docker.

To install, check out the [installation guide](installation.md).

After following the installation guide, you should have a working Kogia instance.

## Workflow

A usual workflow will look like this:

1. Uploading samples, creating a *submission*.
2. Select plugins and create a job to run on the new *submission*
3. View analysis job results
4. Export data to other services and into other formats

## Logging Into Kogia

In a browser, go to `http://127.0.0.1:3000` which should bring up the Kogia web interface.

If configured for authentication, log in with the username and password you set up during installation.

## Submitting a Sample

To submit a sample, click the "Upload" navigation item to go to the upload page.

