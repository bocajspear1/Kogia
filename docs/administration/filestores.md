# Filestores

Filestores are used by Kogia to store files. The exact method is abstracted away for the framework, allowing Kogia to support any number of file storage methods. 

## FileStoreFS

This is the most straightforward filestore type, which simply stores file on the local filesystem.

Files are stored under `<dir>/<SUBMISSION_UUID>`, with any job files stored at `<dir>/<SUBMISSION_UUID>/<JOB_UUID>`. Export files are stored under `<dir>/EXPORT/`

### Configuration

- **dir**: Directory to store files in.