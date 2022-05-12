# What is Kogia?

Kogia is a flexible, modular malware analysis framework. It is built for:

* Highly flexible and adaptable
* Easily extendable data and IOC extraction processes
* Malware sample data analysis 

Kogia seeks to create an analysis engine that is not tied to a single path of analysis.

# Structure

## Signature

A **signature** in Kogia is a very simple thing, a name and a description of what the single identifer signature is about. This keeps signature data small and easy to compare and find connections.

## Plugin

Everything in Kogia's analysis process is a plugin. Plugins have different roles, and some are required to begin analysis. Plugins can utilize Docker to execute certain tools in a isolated environment that can be easily installed and upgraded.

These are the main plugin types:
* **unarchive**: Extracts one or more files from any archive provided to Kogia
* **identify**: This plugin extracts information from provided files for future plugin operation
* **unpack**: This plugin unpacks a sample, allowing better static analysis
* **syscall**: This plugin extracts syscalls and API calls from the sample, either by emulation or execution
* **signature**: This plugin will analyze a given file and provide signatures on the file, either by static analysis, other plugin operations, or analysis of syscall data.
* **metadata**: Provides some sort of metadata about a file

## Submission

A **submission** is something given to Kogia to analyze. This can be one or more files (the term "sample" isn't used because of this). One of the the files will be designated the "primary" executable, which in syscall-extracting plugins is the file executed.