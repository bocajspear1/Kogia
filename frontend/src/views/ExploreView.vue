<script setup>
import MultiSelectButton from '@/components/general/MultiSelectButton.vue';
import FileIcon from '@/components/file/FileIcon.vue';
import MenuButton from '@/components/menu/MenuButton.vue';
import MenuBar from '@/components/menu/MenuBar.vue';
import Notifications from '@/components/general/Notifications.vue'
</script>
    
<template>
<Notifications ref="notifications"></Notifications>
<div class="column is-4 p-3 is-fullheight">
    <div class="box">
        <MultiSelectButton :items="buttons" @click="setSearchType"></MultiSelectButton>
        <div class="field">
            <label class="label">Search {{ search_type }}</label>
            <div class="field has-addons">
                <div class="control is-expanded">
                    <input class="input" type="text" ref="searchInput">
                </div>
                <div class="control">
                    <button :class="is_loading ? 'button is-info is-loading' : 'button is-info' " @click="doSearch()">
                    Search
                    </button>
                </div>
            </div>
        </div>
        <div>
            <div class="list has-hoverable-list-items">
                <div v-for="selected_item in selected_items" class="list-item">
                    <div class="list-item-image p-2">
                        <mdicon name="file-cog" :size="40" v-if="selected_item.type == 'file'"/>
                        <mdicon name="text-box-outline" :size="40" v-if="selected_item.type == 'metadata'"/>
                        <mdicon name="file-cog" :size="40" v-if="selected_item.type == 'event'"/>
                    </div>
                    <div class="list-item-content">
                        <div class="list-item-title">
                            {{ selected_item.display }}
                        </div>
                        <div class="list-item-description">
                            &nbsp;
                        </div>
                    </div>
                    <div class="list-item-controls">
                        <div class="buttons is-right">
                            <button class="button is-danger" @click="removeSelected(selected_item.uuid)">
                                <mdicon name="close" :size="15"/>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div id="results">
            <h3 class="is-size-3">Results</h3>
            <div class="list has-hoverable-list-items">
                <div v-for="file in file_list" class="list-item" :ref="file.uuid">
                    <div class="list-item-image p-2">
                        <FileIcon :file="file"></FileIcon>
                    </div>
                    <div class="list-item-content">
                        <div class="list-item-title">
                            <span title="This file was dropped by an execution instance">
                                <mdicon name="folder-arrow-down" :size="20" v-if="file.dropped" class="m-1"/>
                            </span>
                            {{ file.name }}
                        </div>
                        <div class="list-item-description">
                            <span>{{  file.hash  }}</span>
                            <span class="tag m-1" v-if="file.exec_arch != ''">
                                <strong>Architecture:</strong>&nbsp;{{ file.exec_arch }}
                            </span>
                            <span class="tag m-1" v-if="file.exec_bits != ''">
                                <strong>Bits:</strong>&nbsp;{{ file.exec_bits }}
                            </span>
                            <span class="tag m-1" v-if="file.target_os != ''">
                                <strong>OS:</strong>&nbsp;{{ file.target_os }}
                            </span>
                            <span class="tag m-1" v-if="file.exec_format != ''">
                                <strong>Format:</strong>&nbsp;{{ file.exec_format }}
                            </span>
                            <span class="tag m-1" v-if="file.exec_packer != ''">
                                <strong>Packer:</strong>&nbsp;{{ file.exec_packer }}
                            </span>
                            <span class="tag m-1" v-if="file.exec_arch == '' && file.target_os == ''">
                                <strong>MIME:</strong>&nbsp;{{ file.mime_type }}
                            </span>

                        </div>
                    </div>
                    <div class="list-item-controls">
                        <div class="buttons is-right">
                            <button class="button is-info" @click="openFile(file.uuid)">
                                <mdicon name="open-in-new" :size="15"/>
                            <!-- <span>Edit</span> -->
                            </button>

                            <button class="button is-info" @click="addGraphItem('file', file)">
                                <mdicon name="plus" :size="15" />
                            </button>
                        </div>
                    </div>
                </div>
                <div v-for="metadata in metadata_list" class="list-item">
                    <div class="list-item-image p-2">
                        <mdicon name="text-box-outline" :size="40"/>
                    </div>
                    <div class="list-item-content">
                        <div class="list-item-title">
                            {{ metadata.key }}
                        </div>
                        <div class="list-item-description">
                            <span>{{  metadata.value  }}</span>
                        </div>
                    </div>
                    <div class="list-item-controls">
                        <div class="buttons is-right">
                            <button class="button is-info" @click="addGraphItem('metadata', metadata)">
                                <mdicon name="plus" :size="15"/>
                            </button>
                        </div>
                    </div>
                </div>
            </div>


        </div>
    </div>
    
</div>
<div class="column is-8 is-fullheight">
    <MenuBar>
      <template v-slot:main>
        <MenuButton iconname="cancel" @click="clearItems" tooltip="Clear"></MenuButton>
        <MenuButton iconname="crosshairs" @click="centerGraph" tooltip="Reset"></MenuButton>
        
        
      </template>
    </MenuBar>
    <div id="cy"></div>
</div>
   
</template>

<style scoped>
#cy {
  width: 100%;
  height: 100%;
  display: block;
  background-color: #f5f5f5;
}

.graphnode .file {
    
}

.graphnode .metadata {
    background-color: blue;
}
</style>

<script>
import time from "@/lib/time";
import api from '@/lib/api';
import cytoscape from '@/lib/cytoscape';
import helpers from '@/lib/helpers';

export default {
  data() {
    return {
        search_type: "files",
        buttons: [
            { "text": "File", "icon": "folder-file", "value": "files"},
            { "text": "Metadata", "icon": "table-multiple", "value": "metadata"},
            { "text": "Event", "icon": "cloud-upload-outline", "value": "events"},
        ],
        metadata_list: [],
        file_list: [],
        selected_items: [],
        cy: null,
        start_uuid: "",
        is_loading: false,
        counter: 1
    }
  },
  mounted() {
    this.setupGraph();
  },
  methods: {
    setupGraph() {
        this.cy = cytoscape({
            container: document.getElementById('cy'),
            zoom: 1,
            pan: { x: 0, y: 0 },
            minZoom: 0.1,
            maxZoom: 2,
            style: [
                {
                    "selector": "node[label]",
                    "style": {
                        "label": "data(label)"
                    }
                },
                {
                    "selector": "edge[label]",
                    "style": {
                        "label": "data(label)",
                        "width": 3
                    }
                },
                {
                    "selector": ".file",
                    "style": {
                        "background-color": "red"
                    }
                    
                }
            ]
        });
        console.log(this.cy)
    },
    setSearchType(search_type) {
        this.search_type = search_type;
        this.$refs.searchInput.value = '';
        this.metadata_list = [];
        this.file_list = [];
    },
    doSearch() {
        var self = this;
        var new_value = self.$refs.searchInput.value;
        console.log(new_value);
        self.is_loading = true;

        self.metadata_list = [];
        self.file_list = [];

        if (self.selected_items.length != 0) {
            var last_uuid = self.selected_items[self.selected_items.length-1]['uuid'];
            var last_type = self.selected_items[self.selected_items.length-1]['type'];

            api.get_search_with_start(new_value, self.search_type, last_uuid, last_type,
                function(resp) {
                    var results = resp['results'];

                    for (var r in results) {
                        var result = results[r];
                        console.log(result)
                        for (var i = 1; i < result['vertices'].length; i++) {
                            var vertex = result['vertices'][i];
                            var item_type = '';
                            if (helpers.has_key(vertex, 'key') && helpers.has_key(vertex, 'value')) {
                                item_type = 'metadata';
                            } else if (helpers.has_key(vertex, 'mime_type')) {
                                item_type = 'file';
                                
                            }
                            self.addGraphVertex(item_type, vertex);

                            if (i == result['vertices'].length - 1) {
                                if (item_type == 'file') {
                                    self.file_list.push(vertex);
                                } else if (item_type == 'metadata') {
                                    self.metadata_list.push(vertex);
                                }
                            }
                        }

                        for (var i = 0; i < result['edges'].length; i++) {
                            var edge = result['edges'][i];
                            
                            self.addGraphEdge(edge['_from'].split('/')[1], edge['_to'].split('/')[1]);
                        }


                    }

                    var layout = self.cy.layout({ name: 'circle' });
                    layout.run();
                    
                    
                    
                    // if (self.search_type == 'metadata') {
                    //     self.metadata_list = ;
                    // } else if (self.search_type == 'files') {
                    //     self.file_list = data['results'];
                    // }
                    self.is_loading = false;
                },
                function(status, data) {
                    self.is_loading = false;
                    self.$refs.notifications.addNotification("error", "Upload Error: " + data);
                }
            )
        } else {
            api.get_search(new_value, self.search_type, 
                function(data) {
                    console.log(data)
                    if (self.search_type == 'metadata') {
                        self.metadata_list = data['results'];
                    } else if (self.search_type == 'files') {
                        self.file_list = data['results'];
                    }
                    self.is_loading = false;
                },
                function(status, data) {
                    self.is_loading = false;
                    self.$refs.notifications.addNotification("error", "Upload Error: " + data);
                }
            )
        }
        

        
    },
    openFile(file_uuid) {
        this.$router.push({ name: 'FileSingle', params: { file_uuid: file_uuid } });
    },
    clearItems() {
        this.cy.removeData();
    },
    centerGraph() {
        this.cy.center();
        this.cy.zoom(1);
    },
    addGraphItem(item_type, item_data) {
        console.log("adding graph item")
        
        var label = this.addGraphVertex(item_type, item_data);
        this.selected_items.push({
            "uuid": item_data['uuid'],
            "display": label,
            "type": item_type,
            "data": item_data
        })
    },
    addGraphVertex(item_type, item_data) {
        var classes = ['graphnode'];
        classes.push(item_type); 

        var label = "";
        if (item_type == "file") {
            label = item_data['name'];
        } else if (item_type == "metadata") {
            label = item_data['key'] + ":" + item_data['value'];
        } else if (item_type == "event") {
            
        }

        var x_set = this.cy.width()/2;
        var y_set = this.cy.height()/2;

        console.log(x_set, y_set);

        var vertex_data = { group: 'nodes', data: { id: item_data['uuid'], label: label  }, position: { x: x_set, y: y_set }, classes: classes}

        console.log(vertex_data)

        this.cy.add([
        vertex_data,
        // { group: 'nodes', data: { id: 'n1' }, position: { x: 200, y: 200 } },
        // { group: 'edges', data: { id: 'e0', source: item_data.uuid, target: 'n1' } }
        ]);

        if (this.selected_items.length == 0) {
            this.centerGraph();
        }

        return label;
    },
    addGraphEdge(from, to) {
        this.cy.add([
            { group: 'edges', data: { id: this.counter, source: from, target: to } }
        ]);
        this.counter += 1;
    },
    removeSelected(remove_uuid) {
        var remove_from = null;
        for (var i in this.selected_items) {
            if (this.selected_items[i]['uuid'] == remove_uuid) {
                remove_from = i;
            }
        }
        if (remove_from != null) {
            var deleted = this.selected_items.splice(i);
            for (var i in deleted) {
                var r = this.cy.$("#" + deleted[i]['uuid'] );
                console.log("Removing " + "#" + deleted[i]['uuid'] )
                this.cy.remove(r);
            }
            
        }
    }
  }
}
</script>