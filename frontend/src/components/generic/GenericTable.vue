<template>
    <table class="table is-striped is-fullwidth">
        <thead>
            <tr>
                <th v-for="column in columns">
                    {{ column }}
                </th>
            </tr>
        </thead>
        <tfoot>
            <tr>
                <td :colspan="columns.length">
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

</style>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      "data": [],
      "columns": []
    }
  },
  props: ["data"],
  mounted() {
    console.log("GenericTable loaded")
  },
  methods: {
    doAction() {
    }
  }
}
</script>
