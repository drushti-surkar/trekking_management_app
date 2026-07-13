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
    <div class="row justify-content-center">
      <div class="col-md-5">
        <div class="card shadow-sm mt-5">
          <div class="card-body">
            <h4 class="card-title mb-3 text-success">Login</h4>
            <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
            <form @submit.prevent="submit">
              <div class="mb-3">
                <label class="form-label">Email</label>
                <input v-model="email" type="email" class="form-control" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Password</label>
                <input v-model="password" type="password" class="form-control" required>
              </div>
              <button class="btn btn-success w-100" :disabled="loading">
                {{ loading ? "Logging in..." : "Login" }}
              </button>
            </form>
            <p class="mt-3 mb-0 text-center">
              New trekker? <router-link to="/register">Register here</router-link>
            </p>
          </div>
        </div>
      </div>
    </div>`,
};
