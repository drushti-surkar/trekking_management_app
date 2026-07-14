const Login = {
    data() {
        return { email: "", password: "", error: "", loading: false };
    },
    methods: {
        async submit() {
            this.error = "";
            this.loading = true;
            try {
                const { data } = await axios.post("/api/login", {
                    email: this.email,
                    password: this.password,
                });
                auth.set(data);
                this.$router.push("/" + data.role);
            } catch (e) {
                this.error = e.response?.data?.error || "Login failed.";
            } finally {
                this.loading = false;
            }
        },
    },
    template: `
    <div class="auth-wrap">
      <div class="card auth-card">
        <div class="row g-0">
          <div class="col-md-6 d-none d-md-block">
            <div class="auth-collage">
              <img src="/static/img/hero1.jpg" alt="" onerror="this.style.display='none'">
              <img src="/static/img/hero2.jpg" alt="" onerror="this.style.display='none'">
              <img src="/static/img/hero3.jpg" alt="" onerror="this.style.display='none'">
              <img src="/static/img/hero4.jpg" alt="" onerror="this.style.display='none'">
            </div>
          </div>
          <div class="col-md-6">
            <div class="auth-form-side">
              <h3 class="text-success mb-1">🏔️ Welcome Back</h3>
              <p class="text-muted mb-4">Log in to plan your next trek.</p>
              <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
              <form @submit.prevent="submit">
                <div class="mb-3">
                  <label class="form-label">Email</label>
                  <input v-model="email" type="email" class="form-control form-control-lg" required>
                </div>
                <div class="mb-3">
                  <label class="form-label">Password</label>
                  <input v-model="password" type="password" class="form-control form-control-lg" required>
                </div>
                <button class="btn btn-success btn-lg w-100" :disabled="loading">
                  {{ loading ? "Logging in..." : "Login" }}
                </button>
              </form>
              <p class="mt-4 mb-0 text-center">
                New trekker? <router-link to="/register">Register here</router-link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>`,
};
