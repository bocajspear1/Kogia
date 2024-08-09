# Getting Started

Welcome to Kogia! The Kogia framework is a highly modular and extensible malware analysis framework, built for easy integration of new tools and malware data analysis and exploration.

## Installation 

Kogia is built with Python 3, ArangoDB, and Docker.

To install, check out the [installation guide](installation.md).

## Kogia Fundamentals

### Submissions

Analyses are performed on *Submissions*, which includes one or more files. This allows analysis to be performed with multiple files at a time, needed for certain malware families and techniques. When uploading files, you upload to a *Submission*, then run a *Job* on it. Files can be still accessed directly through the submission they were uploaded in. This also means that files can be uploaded multiple times to different submissions.

### Plugins

Plugins are at the core of Kogia's capabilities. All analysis is performed by plugins. One or more plugins are run in *Jobs*. Plugins come in different types and serve different roles, but each usually peform a since task, such as running a tool against the same or executing the sample in a sandbox to collect syscalls. The use of plugins allows immense flexibility when perform analyses.