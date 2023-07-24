import { defineStore, createPinia } from 'pinia'

export const useUserSession = defineStore('user', {
    state: () => ({
      roles: [],
      api_key: "",
      username: "",
    }),
    getters: {

    },
    actions: {
      updateSession(username, api_key, roles) {
        this.username = username;
        this.api_key = api_key;
        this.roles = roles;
      },
      clearSession() {
        this.username = '';
        this.api_key = '';
        this.roles = [];
      }
    },
    persist: true
  })