# Creating Analysis Jobs

The "New Analysis" page allows a user to create analysis jobs with any number of plugins. 

![](/images/analysis_job_top.png)

Firstly, a "primary file" must be selected from the list of the files in the submission. This file will the file executed during any dynamic analysis. 

At the bottom of the page is three columns of plugins. Each has a checkbox button in their upper right corner. If a check is shown, the plugin will be run against the submission. If an X is shown with the plugin's name greyed out, the plugin will not be run. The three columns of plugins divide the plugins by role:

![](/images/analysis_job_plugins.png)

- **Syscall**: These plugins perform dynamic analysis and extracts activities and system API calls when the primary file is executed. Syscall plugins may also take syscall information and construct _events_ for future analysis. These plugins are run first.

> Note that syscall plugins simply extract syscall information and do not perform any further analysis.

- **Metadata**: These plugins extract data from the submission and insert them into the database. Examples are plugins to extract strings and imported functions. Metadata can be viewed in the web interface or used by signature plugins to identify suspicious activity. These plugins are run second.
- **Signature**: These plugins scan the submission for known malicious indicators or take syscall, event or metadata and compare to malicious indicators. These signatures will appear in the web interface and affect the job's maliciousness score. These plugins are run last.