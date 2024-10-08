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
            if (resp.response != undefined && resp.response != null) {
                if (resp.response.status == 401) {
                    router.push({ name: 'LoginPage'});
                } else {
                    on_failed(resp.response.status, resp.message);
                }
            } else {
                console.log(resp);
                on_failed(500, resp.message);
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
        }).catch(function (error) {
            var resp_data = error.response['data'];
            var error_message = resp_data['error']
            on_failed(error.response.status, error_message); 
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
    do_create_analysis: function(submission_uuid, primary_uuid, plugin_list, ignore_list, on_succeeded, on_failed){
        this.api_post_json('/analysis/new', {
            "submission_uuid": submission_uuid,
            "primary_uuid": primary_uuid,
            "plugins": plugin_list,
            "ignore_uuids": ignore_list
        }, on_succeeded, on_failed);
    },
    // do_submission_upload: function
    get_system_stats: function(on_succeeded, on_failed) {
        this.api_call("/system/stats", on_succeeded, on_failed);
    },
    get_system_usage: function(on_succeeded, on_failed) {
        this.api_call("/system/usage", on_succeeded, on_failed);
    },
    get_system_version: function(on_succeeded, on_failed) {
        this.api_call("/system/version", on_succeeded, on_failed);
    },
    get_runners: function(on_succeeded, on_failed) {
        this.api_call("/system/runners", on_succeeded, on_failed);
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
    get_submission_token: function(submission_uuid, on_succeeded, on_failed) {
        this.api_call("/submission/" + submission_uuid + "/gettoken", on_succeeded, on_failed);
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
    get_job_details: function(job_uuid, on_succeeded, on_failed) {
        this.api_call("/job/" + job_uuid + "/details", on_succeeded, on_failed);
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
    get_file_metadata_list: function(file_uuid, metadata, filter, skip, limit, on_succeeded, on_failed) {
        if (!filter) {   
            this.api_call("/file/" + file_uuid + "/metadata/" + metadata + "/list?skip=" + skip + "&limit=" + limit, on_succeeded, on_failed);
        } else {
            this.api_call("/file/" + file_uuid + "/metadata/" + metadata + "/list?filter=" + filter + "&skip=" + skip + "&limit=" + limit, on_succeeded, on_failed);
        }
    },
    get_job_logs: function(job_uuid, skip, limit, filter, on_succeeded, on_failed) {
        if (!filter) {   
            this.api_call("/job/" + job_uuid + "/logs?skip=" + skip + "&limit=" + limit, on_succeeded, on_failed);
        } else {
            this.api_call("/job/" + job_uuid + "/logs?filter=" + filter + "&skip=" + skip + "&limit=" + limit, on_succeeded, on_failed);
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
    do_job_export: function(job_uuid, plugin_name, export_items, on_succeeded, on_failed){
        this.api_post_json("/job/" + job_uuid + "/export/" + plugin_name, {
            "export_items": export_items
        }, on_succeeded, on_failed);
    },
    get_plugin_list: function(on_succeeded, on_failed) {
        this.api_call("/plugin/list", on_succeeded, on_failed);
    },
    get_plugin_list_type: function(plugin_type, on_succeeded, on_failed) {
        this.api_call("/plugin/list?type=" + plugin_type, on_succeeded, on_failed);
    },
    get_plugin_data: function(plugin_name, on_succeeded, on_failed) {
        this.api_call("/plugin/" + plugin_name + "/info", on_succeeded, on_failed);
    },
    get_plugin_action: function(plugin_name, action, on_succeeded, on_failed) {
        this.api_call("/plugin/" + plugin_name + "/action/" + action, on_succeeded, on_failed);
    },
    get_instance_data: function(instance_uuid, on_succeeded, on_failed) {
        this.api_call("/exec_instance/" + instance_uuid, on_succeeded, on_failed);
    },
    get_instance_metadata_types: function(instance_uuid, on_succeeded, on_failed) {
        this.api_call("/exec_instance/" + instance_uuid  + "/metadata/list", on_succeeded, on_failed);
    },
    get_instance_metadata_list: function(instance_uuid, metadata, filter, skip, limit, on_succeeded, on_failed) {
        if (!filter) {   
            this.api_call("/exec_instance/" + instance_uuid + "/metadata/" + metadata + "/list?skip=" + skip + "&limit=" + limit, on_succeeded, on_failed);
        } else {
            this.api_call("/exec_instance/" + instance_uuid + "/metadata/" + metadata + "/list?filter=" + filter + "&skip=" + skip + "&limit=" + limit, on_succeeded, on_failed);
        }
    },
    get_instance_netcomms: function(skip, limit, instance_uuid, address_filter, port_filter, on_succeeded, on_failed) {
        var call = "/exec_instance/" + instance_uuid  + "/netcomm/list?skip=" + skip.toString() + "&limit=" + limit.toString();
        if (address_filter != "") {
            call += "&address=" + address_filter;
        }
        if (port_filter != "") {
            call += "&port=" + port_filter;
        }
        this.api_call(call, on_succeeded, on_failed);
    },
    get_instance_thumbnail: function(instance_uuid, screenshot_name, on_succeeded, on_failed) {
        this.api_call("/exec_instance/" + instance_uuid  + "/thumbnail/" + screenshot_name, on_succeeded, on_failed);
    },
    get_instance_screenshot: function(instance_uuid, screenshot_name, on_succeeded, on_failed) {
        this.api_call("/exec_instance/" + instance_uuid  + "/screenshot/" + screenshot_name, on_succeeded, on_failed);
    },
    get_process_events: function(skip, limit, process_uuid, type_filter, info_filter, data_filter, on_succeeded, on_failed) {
        var filter_str = "";
        if(type_filter != "") {
            filter_str += "&type=" + type_filter;
        }
        if(info_filter != "") {
            filter_str += "&info=" + info_filter;
        }
        if(data_filter != "") {
            filter_str += "&data=" + data_filter;
        }
        this.api_call("/process/" + process_uuid + "/events?skip=" + skip.toString() + "&limit=" + limit.toString() + filter_str, on_succeeded, on_failed);
    },
    get_process_metadata_types: function(process_uuid, on_succeeded, on_failed) {
        this.api_call("/process/" + process_uuid + "/metadata/list", on_succeeded, on_failed);
    },
    get_process_metadata_list: function(process_uuid, metadata, filter, skip, limit, on_succeeded, on_failed) {
        if (!filter) {   
            this.api_call("/process/" + process_uuid + "/metadata/" + metadata + "/list?skip=" + skip + "&limit=" + limit, on_succeeded, on_failed);
        } else {
            this.api_call("/process/" + process_uuid + "/metadata/" + metadata + "/list?filter=" + filter + "&skip=" + skip + "&limit=" + limit, on_succeeded, on_failed);
        }
    },
    get_process_syscalls: function(process_uuid, skip, limit, on_succeeded, on_failed) {
        this.api_call("/process/" + process_uuid + "/syscalls?skip=" + skip.toString() + "&limit=" + limit.toString(), on_succeeded, on_failed);
    },
    get_docs_page: function(page, on_succeeded, on_failed) {
        this.api_call("/docs/" + page, on_succeeded, on_failed);
    },
    get_search: function(query, item_type, on_succeeded, on_failed) {
        this.api_call("/explore/search?q=" + query + "&type=" + item_type, on_succeeded, on_failed);
    },
    get_search_with_start: function(query, item_type, start_uuid, start_type, on_succeeded, on_failed) {
        this.api_call("/explore/connected/" + start_type + "/"+ start_uuid + "?q=" + query + "&type=" + item_type, on_succeeded, on_failed)
    },
}
