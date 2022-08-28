import axios from 'axios';

export default {
    get_plugin_action: function(plugin_name, action, on_success, on_fail) { 
        axios.get("/api/v1/plugin/" + plugin_name + "/action/" + action).then(function(resp){
            var resp_data = resp['data'];

            if (resp_data['ok'] == true) {
                on_success(resp_data['result'])
            } else {
                on_fail();
            }
            
        }).catch(function(resp){
            on_fail(resp);
        });
    }
}
  