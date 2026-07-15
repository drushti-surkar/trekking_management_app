const App = {
    computed: { auth: () => auth },
    methods: {
        async logout() {
            try { await axios.post("/api/logout"); } catch (e) {  }
            auth.clear();
            this.$router.push("/login");
        },
    },
    template: `
    <div>
      <nav class="navbar navbar-dark bg-success px-3 mb-3">
        <span class="navbar-brand mb-0 h1">
          <svg class="brand-logo" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round">
            <path d="M3 20 L9 8 L13 15 L16 9 L21 20 Z"/>
          </svg>Manzil
        </span>
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
