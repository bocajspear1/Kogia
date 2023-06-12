<script setup>
import Paginator from "../general/Paginator.vue";
</script>

<template>
<div class="container p-2">
    <template v-if="error == null && syscall_list.length > 0">
        <table class="table is-striped is-fullwidth">
        <thead>
            <tr>
                <td colspan="4">
                    <Paginator :item_total="syscall_count" :page_size="page_size" @new_page="onNewPage" :sync_page="syscall_page"></Paginator>
                </td>
            </tr>
            <tr>
                <th>API Name</th>
                <th>Args</th>
                <th>Return Code</th>
                <th>TID</th>
            </tr>
            
        </thead>
        <tfoot>
            <tr>
                <td colspan="4">
                    <Paginator :item_total="syscall_count" :page_size="page_size" @new_page="onNewPage" :sync_page="syscall_page"></Paginator>
                </td>
            </tr>
           
            
        </tfoot>

        <tbody>
            <tr v-for="syscall in syscall_list">
                <td>
                    ({{ syscall.timestamp }}) {{ syscall.name }}
                </td>
                <td class="content m-0">
                    <ul class="m-0">
                        <li v-for="arg in syscall.args">{{ arg }}</li>
                    </ul>
                    
                </td>
                <td>
                    {{ syscall.return_code }} <template v-if="syscall.return_code != 0">(0x{{ syscall.return_code.toString(16) }})</template>
                </td>
                <td>
                    {{ syscall.tid }}
                </td>
            </tr>
        </tbody>
    </table>
    </template>
    <div class="notification is-info" v-else-if="done != false && syscall_list.length == 0">
        No syscalls found
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
        syscall_list: [],
        syscall_page: 1,
        page_size: 30,
        syscall_count: 0
    }
  },
  props: ["process_uuid"],
  mounted() {
    this.getSyscallList();
  },
  watch: {
    'process_uuid' (to, from) {
        this.getSyscallList();
    }
  },
  methods: {
    getSyscallList() {
        var self = this;
        self.done = false;
        api.get_process_syscalls(self.process_uuid, ((self.syscall_page-1) * self.page_size), self.page_size,
            function(data) {
                console.log(data);
                self.syscall_list = data['syscalls'];
                self.syscall_count = data['total'];
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
    },
    onNewPage: function(page_num) {
        console.log(page_num)
        this.syscall_page = page_num;
        this.getSyscallList();
    }
  }
}
</script>