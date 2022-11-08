import axios from 'axios';


export default  {
    api_call: function(path, on_succeeded, on_failed) {
        
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
            console.log(resp_data)
            if (resp_data['ok'] === true) {
                console.log(path, on_succeeded, on_failed);
                on_succeeded(resp_data['result']);
            } else {
                on_failed(200, resp_data['error']);
            }
        }).catch(function(resp){
            console.log(resp);
            on_failed(resp.response.status, resp.message);
        })
    },
    get_job_info: function(job_uuid, on_succeeded, on_failed) {
        this.api_call("/job/" + job_uuid + "/info", on_succeeded, on_failed);
    },
    get_file_info: function(file_uuid, on_succeeded, on_failed) {
        this.api_call("/file/" + file_uuid + "/info", on_succeeded, on_failed);
    }
}
