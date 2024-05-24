<script setup>

</script>
<template>
    <template  v-for="severity in severities" >
        <div v-if="severity.count > 0" :class="'message ' + severity.class " :ref="severity.name">
            <div class="message-header">
                <p>{{ severity.name }} ({{ severity.count }})</p>
                <button class="card-header-icon" aria-label="toggle severity" @click="toggleSeverity(severity.num)" :title="'Show/hide ' + severity.name + ' plugin'">
                    <span class="icon">
                        <mdicon name="chevron-down" :size="30" v-if="severity.enabled == true" />
                        <mdicon name="chevron-up" :size="30" v-if="severity.enabled == false" />
                    </span>
                </button>
            </div>
            <div v-if="severity.enabled" class="message-body">
                <div class="list">
                    <template v-for="signature_match in signature_matches">
                        <div v-if="signature_match.signature.severity == severity.num" class="list-item" :ref="signature_match.signature.uuid">
                        
                            <div class="list-item-image p-2">
                                <mdicon v-if="signature_match.signature.severity == '1'" name="information-variant" :size="30" />
                                <mdicon v-if="signature_match.signature.severity == '2'" name="help" :size="30" />
                                <mdicon v-if="signature_match.signature.severity == '3'" name="alert" :size="30" />
                                <mdicon v-if="signature_match.signature.severity == '4'" name="alert-octagon" :size="30" />
                            </div>
                            <div class="list-item-content">
                                <div class="list-item-title">{{ signature_match.signature.name }} ({{ signature_match.signature.plugin }})</div>
                                <div class="list-item-description">
                                    {{ signature_match.signature.description }}
                                    <template v-for="extra in signature_match.extra">
                                        {{ extra }}
                                    </template>
                                </div>
                            </div>

                        </div>
                    </template>
                    
                </div>
            </div>
            
        </div>
    </template>
    <div class="notification is-info m-2" v-if="signature_matches.length == 0">
        No signatures found
    </div>
    
</template>

<style scoped>
    .is-suspicious {
        background-color: rgb(255, 233, 193);
    }

    .is-suspicious .message-header {
        background-color: orangered;
        color: white;
    }
</style>

<script>
export default {
  data() {
    return {
        current: null,
        severities: [
            { "name": "Malicious", "num": 4, "class": "is-danger", "count": 0, "enabled": false},
            { "name": "Suspicious", "num": 3, "class": "is-suspicious", "count": 0, "enabled": false },
            { "name": "Caution", "num": 2, "class": "is-warning", "count": 0, "enabled": false },
            { "name": "Informational", "num": 1, "class": "is-info", "count": 0, "enabled": false },
        ]
    }
  },
  watch: {
    'signature_matches' (to, from) {
        this.updateCount();
    }
  },
  props: {
    signature_matches: Array,
  },
  mounted() {
    this.updateCount();
  },
  methods: {
    updateCount() {
        for (var i = 0; i < this.severities.length; i++) {
            this.severities[i].count = 0;
        }
        for (var s in this.signature_matches) {
            console.log("hi")
            for (var i = 0; i < this.severities.length; i++) {
                if (this.severities[i].num == this.signature_matches[s].signature.severity) {
                    this.severities[i].count += 1;
                }
            }
        }
    },
    toggleSeverity(num) {
        for (var i = 0; i < this.severities.length; i++) {
            if (this.severities[i].num == num) {
                this.severities[i].enabled = !this.severities[i].enabled;
            }
        }
    },
  }
}
</script>