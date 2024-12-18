<script setup>
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  ArcElement
} from 'chart.js'
import { Line, Pie } from 'vue-chartjs';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  ArcElement
)

</script>

<template>
<div class="container column is-10">
    <button class="button" @click="updateStats">Refresh</button>
    <div class="card" v-for="runner in runners">
        <header class="card-header">
            <p class="card-header-title">{{ runner.name }}</p>
        </header>
        <div class="card-content" v-if="runner.active">
            <div class="content">
                <ul>
                    <li><strong>System:</strong>&nbsp;{{ runner.system }}</li>
                    <li><strong>Running Version:</strong>&nbsp;{{ runner.version }}</li>
                    <li><strong>Job Count:</strong>&nbsp;{{ runner.job_count }}</li>
                </ul>
                <Line :data="runner.cpu_dataset" :options="cpu_graph_options" style="width:49%; display: inline-block;"></Line>
                <Line :data="runner.memory_dataset" :options="memory_graph_options" style="width:49%; display: inline-block;"></Line>
                <Pie :data="runner.localstore_dataset" :options="localstore_pie_options" style="width:40%; display: inline-block;"></Pie>
                <Pie :data="runner.filestore_dataset" :options="filestore_pie_options" style="width:40%; display: inline-block;"></Pie>
            </div>
        </div>
        <div class="card-content" v-else>
            <div class="content">
                <div class="notification is-warning">
                    Runner is likely down!
                </div>
            </div>
        </div>
    </div>
  
</div>
  
</template>

<style scoped>

</style>


<script>
import time from "@/lib/time";
import api from '@/lib/api';
import helpers from '@/lib/helpers';

export default {
  data() {
    return {
        runners: [],
        cpu_graph_options: {
            scales: {
                y: {
                    max: 100,
                    min: 0
                },
                x: {
                    display: false
                }
            },
            responsive: false
        },
        memory_graph_options: {
            scales: {
                y: {
                    max: 100,
                    min: 0
                },
                x: {
                    display: false
                }
            },
            responsive: false
        },
        localstore_pie_options: {
            plugins: {
                title: {
                    display: true,
                    text: 'Local Storage Usage'
                }
            },
            responsive: false
        },
        filestore_pie_options: {
            plugins: {
                title: {
                    display: true,
                    text: 'Filestore Usage'
                }
            },
            responsive: false
        }
        
    }
  },
  mounted() {
    this.updateStats();
  },   
  methods: {

    updateStats() {
        var self = this;
        api.get_runners(function(data) {
            self.runners = data['runners'];


            function compareFn(a, b) {
                if (a['name'] < b['name']) {
                    return -1;
                } else if (a['name'] > b['name']) {
                    return 1;
                }
                return 0;
            }
            self.runners.sort(compareFn);

            for (var i = 0; i < self.runners.length; i++) {

                var now = Math.floor(Date.now() / 1000);
                if (now - self.runners[i]['updated'] >= (60 * 1)) {
                    self.runners[i]['active'] = false;
                } else {
                    self.runners[i]['active'] = true;
                }

                self.runners[i]['cpu_dataset'] = {
                    datasets: [
                        {
                            label: 'CPU Usage',
                            backgroundColor: '#f87979',
                            borderColor: '#f87979',
                            data: self.runners[i]['cpu_usage'],
                            fill: true,
                        }
                    ],
                    labels: self.runners[i]['cpu_usage']
                }
                self.runners[i]['memory_dataset'] = {
                    datasets: [
                        {
                            label: 'Memory Usage',
                            backgroundColor: '#81C784',
                            borderColor: '#81C784',
                            data: self.runners[i]['memory_usage'],
                            fill: true,
                        }
                    ],
                    labels: self.runners[i]['memory_usage']
                }
                var localstore_used = helpers.bytesToGBs(self.runners[i]['localstore_used']);
                var localstore_free = helpers.bytesToGBs(self.runners[i]['localstore_total'] - self.runners[i]['localstore_used']);
                self.runners[i]['localstore_dataset'] = {
                    datasets: [
                        {
                            label: 'Local Disk Usage (' + helpers.bytesToGBs(self.runners[i]['localstore_total']) + "GB)",
                            data: [
                                localstore_used,
                                localstore_free 
                            ],
                            backgroundColor: [
                                "#FF8A65",
                                "#CFD8DC"
                            ]
                        }
                    ],
                    labels: [
                        "Used (" + localstore_used + "GB)",
                        "Free (" + localstore_free + "GB)",
                    ]
                }

                var filestore_used = helpers.bytesToGBs(self.runners[i]['filestore_used']);
                var filestore_free = helpers.bytesToGBs(self.runners[i]['filestore_total'] - self.runners[i]['filestore_used']);
                self.runners[i]['filestore_dataset'] = {
                    datasets: [
                        {
                            label: 'Local Disk Usage',
                            data: [
                                filestore_used,
                                filestore_free
                            ],
                            backgroundColor: [
                                "#4FC3F7",
                                "#CFD8DC"
                            ]
                        }
                    ],
                    labels: [
                        "Used (" + filestore_used + "GB)",
                        "Free (" + filestore_free + "GB)",
                    ]
                }
            }
        },
        function(status, data) {
            self.done = true;
            console.log('FAILURE!!', status, data);
        })
    },
  }
}
</script>