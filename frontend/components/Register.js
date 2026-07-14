const Register = {
    data() {
        return { name: "", email: "", password: "", error: "", loading: false };
    },
    methods: {
        async submit() {
            this.error = "";
            this.loading = true;
            try {
                const { data } = await axios.post("/api/register", {
                    name: this.name,
                    email: this.email,
                    password: this.password,
                });
                auth.set(data);
                this.$router.push("/" + data.role);
            } catch (e) {
                this.error = e.response?.data?.error || "Registration failed.";
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
              <h3 class="text-success mb-1">Join the Trek</h3>
              <p class="text-muted mb-4">Create your trekker account.</p>
              <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
              <form @submit.prevent="submit">
                <div class="mb-3">
                  <label class="form-label">Full Name</label>
                  <input v-model="name" type="text" class="form-control form-control-lg" required>
                </div>
                <div class="mb-3">
                  <label class="form-label">Email</label>
                  <input v-model="email" type="email" class="form-control form-control-lg" required>
                </div>
                <div class="mb-3">
                  <label class="form-label">Password</label>
                  <input v-model="password" type="password" class="form-control form-control-lg"
                         minlength="6" required>
                  <div class="form-text">At least 6 characters.</div>
                </div>
                <button class="btn btn-success btn-lg w-100" :disabled="loading">
                  {{ loading ? "Creating account..." : "Register" }}
                </button>
              </form>
              <p class="mt-4 mb-0 text-center">
                Already have an account? <router-link to="/login">Login</router-link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>`,
};
