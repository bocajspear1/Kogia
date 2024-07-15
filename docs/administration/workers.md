# Workers

Workers process jobs created by users of Kogia. This can range from simple threads to multi-system worker pools. This system is modular to allow a variety of methods of processing jobs.

Each worker will take a job and create a thread to process each file in the job's submission, up to any maximum configured. This parallelizes submission analysis, speeding up response times.

## WorkerThread

This class simply runs jobs on locally hosted threads.

### Configuration

- **max_file**: Maximum number of file threads to spawn at a time.