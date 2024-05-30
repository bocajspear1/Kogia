<script setup>
import Paginator from '@/components/general/Paginator.vue'
</script>

<template>
    <table class="table is-striped is-fullwidth">
        <thead>
            <tr>
                <th v-for="column in columns">
                    {{ column }}
                    <span v-if="!limitFilter.hasOwnProperty(column) && (column.toLowerCase() != 'id' || column.toLowerCase() != 'uuid') && !noFilter.includes(column)">
                        <input class="input is-info" type="text" @input="event => newFilter(column, event.target.value)"/>
                    </span>
                    <div v-if="limitFilter.hasOwnProperty(column)" class="select is-fullwidth">
                        <select>
                            <option selected>Filter {{ column }}</option>
                            <template v-for="value in limitFilter[column]">    
                            <option @click="newFilter(column, value)">{{ value }}</option>
                            </template>
                        </select>
                    </div>
                </th>
            </tr>
            <tr>
                <td :colspan="columns.length">
                    <Paginator :item_total="totalItems" :page_size="pageSize" @new_page="onNewPage" :sync_page="current_page"></Paginator>
                </td>
            </tr>
        </thead>
        <tfoot>
            <tr>
                <td :colspan="columns.length">
                    <Paginator :item_total="totalItems" :page_size="pageSize" @new_page="onNewPage" :sync_page="current_page"></Paginator>
                </td>
            </tr>
        </tfoot>

        <tbody>
            <template v-if="data.length > 0" >
                <tr v-for="row in data">
                    <td class="allow-newlines" v-for="(column, index) in columns">
                        {{ row[index] }}
                    </td>
                </tr>
            </template>
            <template v-else-if="data.length == 0" >
                <tr>
                    <td :colspan="columns.length" >
                        <div class="notification is-warning">
                            No results found
                        </div>
                    </td>
                </tr>
            </template>
        </tbody>
    </table>

   
</template>

<style scoped>
    .allow-newlines {
        white-space: pre-wrap; 
    }
</style>

<script>

export default {
  data() {
    return {
        page: 0,
        current_page: 1
    }
  },
  props: {
    columns: Array,
    data: Array,
    pageSize: Number,
    totalItems: Number,
    noFilter: {
        type: Array,
        default: []
    },
    limitFilter: {
        type: Object,
        default: {}
    },
  },
  emits: ["onFilter", "onNewPage"],
  mounted() {
    
  },
  methods: {
    newFilter: function(column, new_filter) {
        console.log("new filter")
        this.current_page = 1;
        this.$emit("onFilter", column, new_filter);
    },
    onNewPage: function(new_page) {
        this.current_page = new_page;
        this.$emit("onNewPage", new_page);
    }
  }
}
</script>