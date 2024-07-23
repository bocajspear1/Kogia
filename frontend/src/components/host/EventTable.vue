<script setup>
import Paginator from "../general/Paginator.vue";
</script>

<template>
<div class="p-2">
    <template v-if="error == null">
        <table class="table is-striped is-fullwidth fixed-table">
            <colgroup>
                <col class="narrow" />
                <col class="wide" />
                <col class="wide" />
                <col class="status" />
            </colgroup>
            <thead>
                <tr>
                    <th v-if="selectable">Select</th>
                    <th>
                        Event Type
                        <span>
                            <input class="input is-info" type="text" @input="newTypeFilter($event.target.value)"/>
                        </span>
                    </th>
                    <th>
                        Information
                        <span>
                            <input class="input is-info" type="text" @input="newInfoFilter($event.target.value)"/>
                        </span>
                    </th>
                    <th>
                        Data
                        <!-- <span>
                            <input class="input is-info" type="text" @input="newDataFilter($event.target.value)"/>
                        </span> -->
                    </th>
                    <th>Success</th>
                </tr>
                <tr>
                    <td colspan="4">
                        <Paginator :item_total="event_count" :page_size="page_size" @new_page="onNewPage" :sync_page="event_page"></Paginator>
                    </td>
                </tr>
            </thead>
            <tfoot>
                <tr>
                    <td colspan="4">
                        <Paginator :item_total="event_count" :page_size="page_size" @new_page="onNewPage" :sync_page="event_page"></Paginator>
                    </td>
                </tr>
            </tfoot>

            <tbody>
                <tr v-if="event_list.length == 0">
                    <td colspan="4">No events found</td>
                </tr>
                <tr v-for="event in event_list">
                    <td v-if="selectable">
                        <label class="checkbox m-4">
                            <input type="checkbox" @input="eventChecked(event, $event.target.checked)" v-model="event_map[event.uuid]">
                        </label>
                    </td>
                    <td>
                        {{ event.key }}
                    </td>
                    <td class="allow-newlines m-0 limit-data">
                        <ul class="m-0 limit-data">
                            <li v-if="event.src != null && event.src != ''">
                                <strong>Source:</strong> {{ event.src }}
                            </li>
                            <li v-if="event.dest != null && event.dest != ''">
                                <strong>Destination:</strong> {{ event.dest }}
                            </li>
                        </ul>
                    </td>
                    <td class="allow-newlines limit-data" >
                        {{ event.data }}
                    </td>
                    <td>
                        {{ event.success }}
                    </td>
                </tr>
            </tbody>
        </table>
    </template>

</div>
</template>

<style scoped>
.fixed-table {
    table-layout: fixed;
    width: 100%;
}

.fixed-table .wide {
    width: 30%;
}

.fixed-table .narrow {
    width: 20%;
}

.fixed-table .status {
    width: 10%;
}

.limit-data {
    font-size: .9em;
    overflow-wrap: anywhere;
}
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
        page_size: 30,
        event_map: {},
        type_filter: "",
        info_filter: "",
        data_filter: ""
    }
  },
  emits: ["event_checked"],
  props: ["process_uuid", "selectable"],
  mounted() {
    this.getEventList();
  },
  watch: {
    'process_uuid' (to, from) {
        this.getEventList();
        this.event_map = {};
    }
  },
  computed: {
    
  },
  methods: {
    getEventList() {
        var self = this;
        self.done = false;
        api.get_process_events(((self.event_page-1) * self.page_size), self.page_size, self.process_uuid, 
            self.type_filter, self.info_filter, self.data_filter,
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
    },
    eventChecked: function(event, value) {
        this.$emit('event_checked', event, value);
    },
    newTypeFilter: function(value) {
        this.type_filter = value;
        this.getEventList();
    },
    newInfoFilter: function(value) {
        this.info_filter = value;
        this.getEventList();
    },
    newDataFilter: function(value) {
        this.data_filter = value;
        this.getEventList();
    }
  }
}
</script>