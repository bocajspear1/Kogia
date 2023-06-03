<script setup>

</script>

<template>
<div class="container p-2">
    <template v-if="error == null && event_list.length > 0">
        <table class="table is-striped is-fullwidth">
        <thead>
            <tr>
                <th>Event Type</th>
                <th>Information</th>
                <th>Data</th>
            </tr>
        </thead>
        <tfoot>
            <tr>
                <td colspan="3">
                    <nav class="pagination is-centered" role="navigation" aria-label="pagination">
                        <a class="pagination-previous">Previous</a>
                        <a class="pagination-next">Next page</a>
                        <ul class="pagination-list">
                            <li><a class="pagination-link" aria-label="Goto page 1">1</a></li>
                            <li><span class="pagination-ellipsis">&hellip;</span></li>
                            <li><a class="pagination-link" aria-label="Goto page 45">45</a></li>
                            <li><a class="pagination-link is-current" aria-label="Page 46" aria-current="page">46</a></li>
                            <li><a class="pagination-link" aria-label="Goto page 47">47</a></li>
                            <li><span class="pagination-ellipsis">&hellip;</span></li>
                            <li><a class="pagination-link" aria-label="Goto page 86">86</a></li>
                        </ul>
                    </nav>
                </td>
            </tr>
           
            
        </tfoot>

        <tbody>
            <tr v-for="event in event_list">
                <td>
                    {{ event.key }}
                </td>
                <td class="content m-0">
                    <ul class="m-0">
                        <li v-if="event.src != null && event.src != ''">
                            <strong>Source:</strong> {{ event.src }}
                        </li>
                        <li v-if="event.dest != null && event.dest != ''">
                            <strong>Destination:</strong> {{ event.dest }}
                        </li>
                    </ul>
                </td>
                <td class="allow-newlines" >
                    {{ event.data }}
                </td>
            </tr>
        </tbody>
    </table>
    </template>
    <div class="notification is-info" v-else-if="done != false && event_list.length == 0">
        No events found
    </div>
</div>
</template>

<style scoped>

</style>

<script>
import api from "@/lib/api";

export default {
  data() {
    return {
        done: false,
        error: null,
        event_list: [],
        event_page: 0,
        event_count: 0
    }
  },
  props: ["process_uuid"],
  mounted() {
    this.getEventList();
  },
  watch: {
    'process_uuid' (to, from) {
        this.getEventList();
    }
  },
  methods: {
    getEventList() {
        var self = this;
        self.done = false;
        api.get_process_events(self.process_uuid,
            function(data) {
                console.log(data);
                self.event_list = data;
                self.done = true;
            },
            function(status, data) {

            }
        )
    },
    updateSelectFilter(filter) {
        var self = this;
        if (self.file_uuid != null) {
            if (self.selected_type == "") {
                self.selected_type = " ";
            }
            api.get_file_metadata_list(self.file_uuid, self.selected_type, filter,
                function(data){
                    self.error = null;
                    self.metadata_list = [];
                    for (var i = 0; i < data.length; i++) {
                        self.metadata_list.push([data[i]])
                    }
                    
                },
                function(status, data){
                    self.error = data;
                }
            )
        } else if (self.process_uuid != null) {
            if (self.selected_type == "") {
                self.selected_type = " ";
            }
            api.get_process_metadata_list(self.file_uuid, self.selected_type, filter,
                function(data){
                    self.error = null;
                    self.metadata_list = [];
                    for (var i = 0; i < data.length; i++) {
                        self.metadata_list.push([data[i]])
                    }
                    
                },
                function(status, data){
                    self.error = data;
                }
            )
        }
    },
    onFilter: function(column, new_filter) {
        this.updateSelectFilter(new_filter)
    }
  }
}
</script>