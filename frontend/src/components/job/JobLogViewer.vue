<script setup>
import DynamicFilterTable from '@/components/dynamic/DynamicFilterTable.vue';
</script>

<template>
    <DynamicFilterTable v-if="loaded" :columns="['Severity', 'Name', 'Message']" 
                                :data="logs" 
                                :noFilter="['Message']"
                                :limitFilter="{'Severity':['error', 'warning', 'debug', 'info']}"
                                :pageSize="limit"
                                :totalItems="log_count"
                                @onFilter="onLogFilter" @onNewPage="onNewPage"></DynamicFilterTable>
    <progress v-if="!loaded"  class="progress is-small is-primary" max="100">15%</progress>
</template>

<style scoped>
   
</style>

<script>
import api from '@/lib/api';

export default {
    data() {
        return {
            logs: [],
            log_count: 0,
            loaded: false,
            current_page: 1,
            limit: 20,
            filter: ""
        }
    },
    props: ["job_uuid"],
    mounted() {
        this.getLogs("");
    },
    methods: {
        getLogs() {
            var self = this;
            
            self.logs = [];
            api.get_job_logs(self.job_uuid, (self.current_page-1)*self.limit, self.limit, self.filter, 
                function(data) {
                    var log_list = data['logs'];
                    self.log_count = data['total'];
                    console.log(data)
                    for (var i = 0; i < log_list.length; i++) {
                        var message = log_list[i]['message']
                        self.logs.push([log_list[i]['severity'], log_list[i]['log_name'], message]);
                    }
                    self.loaded = true;
                },
                function(status, data) {

                }
            )
        },
        onLogFilter(column, new_filter) {
            console.log(column, new_filter);
        },
        onNewPage(new_page) {
            this.current_page = new_page;
            this.getLogs();
        },
    }
}
</script>
