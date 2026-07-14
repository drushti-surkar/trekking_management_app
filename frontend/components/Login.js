const Login = {
    data() {
        return { email: "", password: "", error: "", loading: false, mode: "trekker" };
    },
    methods: {
        setMode(m) {
            this.mode = m;
            this.error = "";
        },
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
          <div class="col-md-6 d-none d-md-block auth-media">
            <div class="auth-collage">
              <img src="/static/img/hero1.jpg" alt="" onerror="this.style.display='none'">
              <img src="/static/img/hero2.jpg" alt="" onerror="this.style.display='none'">
              <img src="/static/img/hero3.jpg" alt="" onerror="this.style.display='none'">
              <img src="/static/img/hero4.jpg" alt="" onerror="this.style.display='none'">
            </div>
            <div class="auth-overlay">
              <h1 class="brand">Manzil</h1>
              <p class="brand-sub">Trekking Management App</p>
              <p class="brand-quote">"Every mountain top is within reach if you just keep climbing."</p>
            </div>
          </div>
          <div class="col-md-6">
            <div class="auth-form-side">
              <div class="d-md-none text-center mb-3">
                <h2 class="text-success mb-0">Manzil</h2>
                <div class="text-muted small text-uppercase" style="letter-spacing:2px">Trekking Management App</div>
              </div>

              <div class="btn-group w-100 mb-4" role="group">
                <button type="button" @click="setMode('trekker')"
                        :class="mode==='trekker' ? 'btn btn-success' : 'btn btn-outline-success'">Trekker</button>
                <button type="button" @click="setMode('staff')"
                        :class="mode==='staff' ? 'btn btn-success' : 'btn btn-outline-success'">Staff / Admin</button>
              </div>

              <h4 class="mb-1">{{ mode==='trekker' ? 'Welcome Back' : 'Staff & Admin Login' }}</h4>
              <p class="text-muted mb-4">
                {{ mode==='trekker'
                    ? 'Log in to plan your next trek.'
                    : 'Log in with the credentials provided by your administrator.' }}
              </p>
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
              <p v-if="mode==='trekker'" class="mt-3 mb-0 text-center">
                New trekker? <router-link to="/register">Register here</router-link>
              </p>
              <p v-else class="mt-3 mb-0 text-center text-muted small">
                Staff accounts are created by the admin. Contact them if you need access.
              </p>

              <hr class="my-4">
              <div class="row text-center g-2 auth-features">
                <div class="col-4 feat">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round">
                    <path d="M3 20 L9 8 L13 15 L16 9 L21 20 Z"/>
                  </svg>
                  <span class="feat-label">Discover Treks</span>
                </div>
                <div class="col-4 feat">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round">
                    <rect x="3" y="4" width="18" height="17" rx="2"/>
                    <path d="M3 9 H21 M8 2 V6 M16 2 V6 M9 15 l2 2 l4 -4"/>
                  </svg>
                  <span class="feat-label">Easy Booking</span>
                </div>
                <div class="col-4 feat">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round">
                    <path d="M5 21 V4 M5 4 C9 1 13 7 19 4 V13 C13 16 9 10 5 13"/>
                  </svg>
                  <span class="feat-label">Track Journey</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>`,
};
