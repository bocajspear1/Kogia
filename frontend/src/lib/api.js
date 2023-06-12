import axios from 'axios';


export default  {
    api_call_raw: function(path, on_succeeded, on_failed) {
        let data = {
            headers: { }
        }
        var full_path = "/api/v1";
        if (path[0] != "/") {
            full_path += "/";
        }
        
        full_path += path;
        axios.get(full_path, data).then(function(resp){
            var resp_data = resp['data'];
            on_succeeded(resp_data);
        }).catch(function(resp){
            on_failed(resp.response.status, resp.message);
        });
    },
    api_call: function(path, on_succeeded, on_failed) {
        this.api_call_raw(path, 
        function(resp_data){
            // console.log(resp_data)
            if (resp_data['ok'] === true) {
                // console.log(path, on_succeeded, on_failed);
                on_succeeded(resp_data['result']);
            } else {
                on_failed(200, resp_data['error']);
            }
        }, 
        function(resp) {
            if (resp == 404) {
                on_failed(404, "Not Found");
            } else {
                on_failed(resp.response.status, resp.message);
            }
        });
    },
    get_system_stats: function(on_succeeded, on_failed) {
        this.api_call("/system/stats", on_succeeded, on_failed);
    },
    get_system_usage: function(on_succeeded, on_failed) {
        this.api_call("/system/usage", on_succeeded, on_failed);
    },
    get_submission_list: function(file_uuid, on_succeeded, on_failed) {
        if (!file_uuid) {   
            this.api_call("/submission/list", on_succeeded, on_failed);
        } else {
            this.api_call("/submission/list?file=" + file_uuid, on_succeeded, on_failed);
        }
    },
    get_job_list: function(skip, limit, submission_uuid, on_succeeded, on_failed) {
        var url_string = "/job/list?skip=" + skip.toString() + "&limit=" + limit.toString()
        if (submission_uuid != "" && submission_uuid != null) {
            url_string += "&submission=" + submission_uuid;;
        }
        this.api_call(url_string, on_succeeded, on_failed);
    },
    get_job_info: function(job_uuid, on_succeeded, on_failed) {
        this.api_call("/job/" + job_uuid + "/info", on_succeeded, on_failed);
    },
    get_file_info: function(file_uuid, on_succeeded, on_failed) {
        this.api_call("/file/" + file_uuid + "/info", on_succeeded, on_failed);
    },
    get_file_hexdata: function(file_uuid, on_succeeded, on_failed) {
        this.api_call_raw("/file/" + file_uuid + "/download?format=hex", on_succeeded, on_failed);
    },
    get_file_metadata_types: function(file_uuid, on_succeeded, on_failed) {
        this.api_call("/file/" + file_uuid + "/metadata/list", on_succeeded, on_failed);
    },
    get_file_metadata_list: function(file_uuid, metadata, filter, on_succeeded, on_failed) {
        if (!filter) {   
            this.api_call("/file/" + file_uuid + "/metadata/" + metadata + "/list", on_succeeded, on_failed);
        } else {
            this.api_call("/file/" + file_uuid + "/metadata/" + metadata + "/list?filter=" + filter, on_succeeded, on_failed);
        }
    },
    get_job_logs: function(job_uuid, filter, on_succeeded, on_failed) {
        if (!filter) {   
            this.api_call("/job/" + job_uuid + "/logs", on_succeeded, on_failed);
        } else {
            this.api_call("/job/" + job_uuid + "/logs?filter=" + filter, on_succeeded, on_failed);
        }
    },
    get_job_reports: function(job_uuid, file_uuid, on_succeeded, on_failed) {
        if (!file_uuid) {   
            this.api_call("/job/" + job_uuid + "/reports", on_succeeded, on_failed);
        } else {
            this.api_call("/job/" + job_uuid + "/reports?file=" + file_uuid, on_succeeded, on_failed);
        }
    },
    get_report: function(report_uuid, on_succeeded, on_failed) {
        this.api_call("/report/" + report_uuid, on_succeeded, on_failed);
    },
    get_job_signatures: function(job_uuid, file_uuid, on_succeeded, on_failed) {
        if (!file_uuid) {   
            this.api_call("/job/" + job_uuid + "/signatures", on_succeeded, on_failed);
        } else {
            this.api_call("/job/" + job_uuid + "/signatures?file=" + file_uuid, on_succeeded, on_failed);
        }
    },
    get_job_exec_instances: function(job_uuid, on_succeeded, on_failed) {
        this.api_call("/job/" + job_uuid + "/exec_instances", on_succeeded, on_failed);
    },
    get_plugin_data: function(plugin_name, on_succeeded, on_failed) {
        this.api_call("/plugin/" + plugin_name + "/info", on_succeeded, on_failed);
    },
    get_exec_instance_data: function(plugin_name, on_succeeded, on_failed) {
        this.api_call("/exec_instance/" + plugin_name, on_succeeded, on_failed);
    },
    get_process_events: function(process_uuid, on_succeeded, on_failed) {
        this.api_call("/process/" + process_uuid + "/events", on_succeeded, on_failed);
    },
    get_process_metadata_types: function(process_uuid, on_succeeded, on_failed) {
        this.api_call("/process/" + process_uuid + "/metadata/list", on_succeeded, on_failed);
    },
    get_process_metadata_list: function(process_uuid, metadata, filter, on_succeeded, on_failed) {
        if (!filter) {   
            this.api_call("/process/" + process_uuid + "/metadata/" + metadata + "/list", on_succeeded, on_failed);
        } else {
            this.api_call("/process/" + process_uuid + "/metadata/" + metadata + "/list?filter=" + filter, on_succeeded, on_failed);
        }
    },
    get_process_syscalls: function(process_uuid, skip, limit, on_succeeded, on_failed) {
        this.api_call("/process/" + process_uuid + "/syscalls?skip=" + skip.toString() + "&limit=" + limit.toString(), on_succeeded, on_failed);
    },
}
