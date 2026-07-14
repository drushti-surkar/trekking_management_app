const App = {
    computed: { auth: () => auth },
    methods: {
        async logout() {
            try { await axios.post("/api/logout"); } catch (e) { /* ignore */ }
            auth.clear();
            this.$router.push("/login");
        },
    },
    template: `
    <div>
      <nav class="navbar navbar-dark bg-success px-3 mb-3">
        <span class="navbar-brand mb-0 h1">🏔️ Trekking Management</span>
        <div v-if="auth.isAuthed()" class="d-flex align-items-center">
          <span class="text-white me-3">{{ auth.name }} <small>({{ auth.role }})</small></span>
          <button class="btn btn-sm btn-light" @click="logout">Logout</button>
        </div>
      </nav>
      <div class="container">
        <router-view></router-view>
      </div>
    </div>`,
};

Vue.createApp(App).use(router).mount("#app");
