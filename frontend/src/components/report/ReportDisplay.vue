<script setup>

</script>

<template>
<div class="container p-4">
    <div v-if="error != null" class="notification is-warning">
        {{ error }}
    </div>
    <template v-else-if="error == null && file_uuid != null">
        <div class="select is-fullwidth">
            <select ref="reportSelect" @change="onSelect">
                <option selected value="">Select Report</option>
                <template v-for="report in report_list">    
                <option :value="report.uuid">{{ report.name }}</option>
                </template>
            </select>
        </div>
        <div v-if="selected_report != ''">
            <pre>
{{ report_data }}
            </pre>
        </div>
        <div v-if="selected_report == ''">
            <div class="notification is-warning m-2">
                Select report
            </div>
        </div>
    </template>
    <div class="notification is-info m-2" v-else>
        Select a file to view reports
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
        report_list: [],
        selected_report: "",
        report_data: ""
    }
  },
  props: ["file_uuid", "job_uuid"],
  mounted() {
    
    this.getReports();
  

  },
  watch: {
    'file_uuid' (to, from) {
        this.report_list = [];
        this.getReports();
        if (this.selected_report != "") {
            this.$refs.reportSelect.selectedIndex = 0;
        }
        
        this.selected_report = "";
    }
  },
  methods: {
    getReports() {
        var self = this;
        if (self.file_uuid != null) {
            api.get_job_reports(self.job_uuid, self.file_uuid, 
                function(data) {
                    self.report_list = data;
                },
                function(status, data) {

                }
            )
        }
    },
    onSelect(event) {
        if (event.target.value != "") {
            this.selected_report = event.target.value;
            this.updateReportData();
        }
    },
    updateReportData() {
        var self = this;
        if (self.file_uuid != null) {
            api.get_report(this.selected_report,
                function(data){
                    self.error = null;
                    self.report_data = data['value'];
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