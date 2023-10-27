import axios from 'axios';
import { getCurrentInstance } from 'vue';
import router from '../router'
import { useUserSession } from '@/lib/store';

function getFullPath(in_path) {
    let full_path = "/api/v1";
    if (in_path[0] != "/") {
        full_path += "/";
    }
    full_path += in_path;
    return full_path
}

export default  {
    api_call_raw: function(path, on_succeeded, on_failed) {
        let data = {
            headers: { }
        }
        
        let session = useUserSession();
        
        let api_key = session.api_key;
        data.headers['X-Kogia-API-Auth'] = api_key;
        
        let full_path = getFullPath(path);
        axios.get(full_path, data).then(function(resp){
            var resp_data = resp['data'];
            on_succeeded(resp_data);
        }).catch(function(resp){
            if (resp.response != null && resp.response.status == 401) {
                router.push({ name: 'LoginPage'});
            } else {
                on_failed(resp.response.status, resp.message);
            }
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
            } else if (resp == 500) {
                on_failed(500, "Backend error. Please see console and submit a bug report!");
            } else {
                on_failed(resp.response.status, resp.message);
            }
        });
    },
    api_post_raw(path, start_headers, post_data, on_succeeded, on_failed) {
        let config_data = {
            headers: start_headers
        }
        let full_path = getFullPath(path);

        let session = useUserSession();
        let api_key = session.api_key;
        config_data.headers['X-Kogia-API-Auth'] = api_key;
        
        axios.post(full_path, post_data, 
            config_data
        ).then(function (resp) {
            var resp_data = resp['data'];
            if (resp_data['ok'] === true) {
                on_succeeded(resp_data['result']);
            } else {
                on_failed(200, resp_data['error']);
            }
        }).catch(function (resp) {
            on_failed(resp.response.status, resp.message); 
        });
    },
    api_post_json(path, post_data, on_succeeded, on_failed) {
        this.api_post_raw(path, { 
            'Content-Type': 'application/json'
        }, post_data, on_succeeded, on_failed);
    },
    api_post_form(path, post_data, on_succeeded, on_failed) {
        this.api_post_raw(path, { 
            'Content-Type': 'multipart/form-data'
        }, post_data, on_succeeded, on_failed);
    },
    do_login: function(username, password, on_succeeded, on_failed){
        this.api_post_form('/authenticate', {
            username: username,
            password: password
        }, on_succeeded, on_failed);
    },
    do_create_analysis: function(submission_uuid, primary_uuid, plugin_list, on_succeeded, on_failed){
        this.api_post_json('/analysis/new', {
            "submission_uuid": submission_uuid,
            "primary_uuid": primary_uuid,
            "plugins": plugin_list
        }, on_succeeded, on_failed);
    },
    // do_submission_upload: function
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
    get_submission_info: function(submission_uuid, on_succeeded, on_failed) {
        this.api_call("submission/" + submission_uuid + "/info", on_succeeded, on_failed);
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
    get_file_token: function(file_uuid, on_succeeded, on_failed) {
        this.api_call("/file/" + file_uuid + "/gettoken", on_succeeded, on_failed);
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
    get_plugin_list: function(on_succeeded, on_failed) {
        this.api_call("/plugin/list", on_succeeded, on_failed);
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
