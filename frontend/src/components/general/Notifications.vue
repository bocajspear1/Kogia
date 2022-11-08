<template>
    <div id="notification-panel" class="is-overlay">
        <div v-for="(notification, index) in notifications">
            <template v-if="notification.importance=='debug'">
            <div class="notification m-3">
                <button class="delete" @click="closeNotification(index)"></button>
                {{ notification.message }}
            </div>
            </template>
            <template v-if="notification.importance=='error'">
            <div class="notification is-danger  m-3">
                <button class="delete" @click="closeNotification(index)"></button>
                {{ notification.message }}
            </div>
            </template>
            <template v-if="notification.importance=='info'">
            <div class="notification is-info  m-3">
                <button class="delete" @click="closeNotification(index)"></button>
                {{ notification.message }}
            </div>
            </template>
            
        </div>
    </div>
</template>

<style scoped>
    #notification-panel {
        width: 75%;
        margin-right: auto;
        margin-left: auto;
        position: fixed;
        z-index: 999;
        height: 0px;
        overflow: visible;
    }
</style>

<script>
export default {
  data() {
    return {
      notifications: []
    }
  },
  mounted() {
    
  },
  methods: {
    addNotification(importance, message) {
        console.log(importance, message)
        this.notifications.push({"importance": importance, "message": message})
    },
    closeNotification(index) {
        this.notifications.splice(index, 1);
    }
    
  }
}
</script>
