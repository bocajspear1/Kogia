# Viewing Results

Jobs can be viewed by going to "Jobs" and selecting a job. Two types of jobs can exist, a identification job and analysis job. Identification jobs occur automatically on new files submitted to Kogia with unpacking, unarchiving, and identification plugins. Identification jobs will indicate their success in the leftmost column of the job list. Files extracted by static and dynamic analysis also have identification jobs created for them. Analysis jobs are the jobs created by users using syscall, metadata, and signature plugins. Analysis jobs will have a maliciousness score in the leftmost column, in range from 0 (not malicious at all) to 100 (highly malicious).

## Job Results View

![](/images/job_results_main.png)

The sidebar provides links to view different aspects of the analysis.

- **Overview**: Shows the submission and job information. Also shows the signatures matched during the analysis.
- **Host Activity**: Shows data from dynamical analysis plugins, such as syscalls, events, processes, and other metadata related to execution. Each dynamic analysis/syscall plugin is stored as an "execution instance."
- **Network Activity**: Shows network data recorded during dynamical analysis.
- **Files**: Shows files submitted to the job as well as any other files extracted during dynamic and static analysis.
- **Metdata**: Allows the user to view metadata related to individual files, execution instances, and processes.
- **Reports**: Shows reports produced by plugins. Reports are free-form, commonly larger, sets of data for viewing by users instead of by automated systems.
- **Logs**: Lists log messages from the job's analysis.
- **Details**: Provides the details of the job, including the plugins selected and their arguments used for the job.
- **Export**: Shows the export panel for exporting the current job's data for external display, storage, or integration with another system.