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
    <div class="row justify-content-center">
      <div class="col-md-5">
        <div class="card shadow-sm mt-5">
          <div class="card-body">
            <h4 class="card-title mb-3 text-success">Trekker Registration</h4>
            <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
            <form @submit.prevent="submit">
              <div class="mb-3">
                <label class="form-label">Full Name</label>
                <input v-model="name" type="text" class="form-control" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Email</label>
                <input v-model="email" type="email" class="form-control" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Password</label>
                <input v-model="password" type="password" class="form-control"
                       minlength="6" required>
                <div class="form-text">At least 6 characters.</div>
              </div>
              <button class="btn btn-success w-100" :disabled="loading">
                {{ loading ? "Creating account..." : "Register" }}
              </button>
            </form>
            <p class="mt-3 mb-0 text-center">
              Already have an account? <router-link to="/login">Login</router-link>
            </p>
          </div>
        </div>
      </div>
    </div>`,
};
