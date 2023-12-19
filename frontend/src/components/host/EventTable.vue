<script setup>
import Paginator from "../general/Paginator.vue";
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
            <tr>
                <td colspan="3">
                    <Paginator :item_total="event_count" :page_size="page_size" @new_page="onNewPage" :sync_page="event_page"></Paginator>
                </td>
            </tr>
        </thead>
        <tfoot>
            <tr>
                <td colspan="3">
                    <Paginator :item_total="event_count" :page_size="page_size" @new_page="onNewPage" :sync_page="event_page"></Paginator>
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
        event_page: 1,
        event_count: 0,
        page_size: 30
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
        api.get_process_events(((self.event_page-1) * self.page_size), self.page_size, self.process_uuid,
            function(data) {
                self.event_count = data['total'];
                self.event_list = data['events'];
                self.done = true;
            },
            function(status, data) {

            }
        )
    },
    updateSelectFilter(filter) {
        var self = this;

    },
    onFilter: function(column, new_filter) {
        this.updateSelectFilter(new_filter)
    },
    onNewPage: function(page_num) {
        this.event_page = page_num;
        this.getEventList();
    }
  }
}
</script>