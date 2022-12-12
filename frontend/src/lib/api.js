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
            on_failed(resp.response.status, resp.message);
        })
        
    },
    get_submission_list: function(file_uuid, on_succeeded, on_failed) {
        if (!file_uuid) {   
            this.api_call("/submission/list", on_succeeded, on_failed);
        } else {
            this.api_call("/submission/list?file=" + file_uuid, on_succeeded, on_failed);
        }
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
}
