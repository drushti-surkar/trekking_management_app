const TrekkerDashboard = {
    data() {
        return {
            tab: "browse",
            treks: [],
            bookings: [],
            filters: { q: "", difficulty: "", location: "", max_duration: "" },
            profile: { name: "", email: "", password: "" },
            profileMsg: "",
            error: "",
        };
    },
    computed: { auth: () => auth },
    methods: {
        async loadTreks() {
            const params = {};
            for (const [k, v] of Object.entries(this.filters)) if (v) params[k] = v;
            this.treks = (await axios.get("/api/trekker/treks", { params })).data;
        },
        async loadBookings() {
            this.bookings = (await axios.get("/api/trekker/bookings")).data;
        },
        async loadProfile() {
            const { data } = await axios.get("/api/trekker/profile");
            this.profile = { name: data.name, email: data.email, password: "" };
        },
        switchTab(t) {
            this.tab = t;
            if (t === "browse") this.loadTreks();
            if (t === "bookings") this.loadBookings();
            if (t === "profile") this.loadProfile();
        },
        resetFilters() {
            this.filters = { q: "", difficulty: "", location: "", max_duration: "" };
            this.loadTreks();
        },
        async bookTrek(t) {
            try {
                await axios.post("/api/trekker/bookings", { trek_id: t.id });
                await this.loadTreks();
            } catch (e) {
                alert(e.response?.data?.error || "Could not book this trek.");
            }
        },
        async cancelBooking(b) {
            if (!confirm(`Cancel your booking for "${b.trek_name}"?`)) return;
            try {
                await axios.patch(`/api/trekker/bookings/${b.id}/cancel`);
                this.loadBookings();
            } catch (e) {
                alert(e.response?.data?.error || "Could not cancel.");
            }
        },
        async saveProfile() {
            this.error = ""; this.profileMsg = "";
            try {
                const { data } = await axios.put("/api/trekker/profile", {
                    name: this.profile.name,
                    password: this.profile.password || undefined,
                });
                this.profile.password = "";
                this.profileMsg = "Profile updated.";
                auth.name = data.name;
                localStorage.setItem("tma_name", data.name);
            } catch (e) {
                this.error = e.response?.data?.error || "Could not update profile.";
            }
        },
        badgeClass(status) {
            return {
                Booked: "bg-primary", Completed: "bg-success",
                Cancelled: "bg-secondary",
            }[status] || "bg-secondary";
        },
    },
    mounted() { this.loadTreks(); },
    template: `
    <div>
      <h3 class="text-success mb-3">Trekker Dashboard</h3>

      <ul class="nav nav-tabs mb-3">
        <li class="nav-item" v-for="t in [['browse','Browse Treks'],['bookings','My Bookings'],['profile','Profile']]" :key="t[0]">
          <a class="nav-link" :class="{active: tab===t[0]}" href="#" @click.prevent="switchTab(t[0])">{{ t[1] }}</a>
        </li>
      </ul>

      <!-- BROWSE -->
      <div v-if="tab==='browse'">
        <div class="card card-body mb-3">
          <div class="row g-2">
            <div class="col-md-3"><input v-model="filters.q" @input="loadTreks" class="form-control" placeholder="Trek name"></div>
            <div class="col-md-3"><input v-model="filters.location" @input="loadTreks" class="form-control" placeholder="Location"></div>
            <div class="col-md-3">
              <select v-model="filters.difficulty" @change="loadTreks" class="form-select">
                <option value="">Any difficulty</option>
                <option>Easy</option><option>Moderate</option><option>Hard</option>
              </select>
            </div>
            <div class="col-md-2"><input type="number" min="1" v-model="filters.max_duration" @input="loadTreks" class="form-control" placeholder="Max days"></div>
            <div class="col-md-1"><button class="btn btn-outline-secondary w-100" @click="resetFilters">Clear</button></div>
          </div>
        </div>

        <div class="row g-3">
          <div class="col-md-6 col-lg-4" v-for="t in treks" :key="t.id">
            <div class="card h-100 shadow-sm">
              <div class="card-body d-flex flex-column">
                <h5 class="card-title text-success mb-1">{{ t.name }}</h5>
                <div class="text-muted mb-2">📍 {{ t.location }}</div>
                <ul class="list-unstyled small mb-3">
                  <li><strong>Difficulty:</strong> {{ t.difficulty }}</li>
                  <li><strong>Duration:</strong> {{ t.duration_days }} days</li>
                  <li><strong>Available:</strong> {{ t.available_slots }}/{{ t.total_slots }} slots</li>
                  <li v-if="t.start_date"><strong>Starts:</strong> {{ t.start_date }}</li>
                </ul>
                <div class="mt-auto">
                  <button v-if="t.already_booked" class="btn btn-outline-success w-100" disabled>✓ Booked</button>
                  <button v-else-if="t.available_slots<=0" class="btn btn-outline-secondary w-100" disabled>Full</button>
                  <button v-else class="btn btn-success w-100" @click="bookTrek(t)">Book Now</button>
                </div>
              </div>
            </div>
          </div>
          <div v-if="!treks.length" class="col-12 text-center text-muted py-4">No open treks match your filters.</div>
        </div>
      </div>

      <!-- MY BOOKINGS -->
      <div v-if="tab==='bookings'">
        <div class="table-responsive">
          <table class="table table-striped align-middle">
            <thead><tr>
              <th>Trek</th><th>Location</th><th>Difficulty</th><th>Booked On</th>
              <th>Trek Status</th><th>Booking</th><th></th>
            </tr></thead>
            <tbody>
              <tr v-for="b in bookings" :key="b.id">
                <td>{{ b.trek_name }}</td><td>{{ b.location }}</td><td>{{ b.difficulty }}</td>
                <td>{{ (b.booking_date||'').slice(0,10) }}</td>
                <td><span class="badge bg-info text-dark">{{ b.trek_status }}</span></td>
                <td><span class="badge" :class="badgeClass(b.status)">{{ b.status }}</span></td>
                <td>
                  <button v-if="b.status==='Booked'" class="btn btn-sm btn-outline-danger" @click="cancelBooking(b)">Cancel</button>
                </td>
              </tr>
              <tr v-if="!bookings.length"><td colspan="7" class="text-center text-muted">No bookings yet.</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- PROFILE -->
      <div v-if="tab==='profile'" class="row justify-content-center">
        <div class="col-md-6">
          <div class="card shadow-sm">
            <div class="card-body">
              <h5 class="text-success mb-3">My Profile</h5>
              <div v-if="profileMsg" class="alert alert-success py-2">{{ profileMsg }}</div>
              <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
              <div class="mb-3">
                <label class="form-label">Email</label>
                <input :value="profile.email" class="form-control" disabled>
              </div>
              <div class="mb-3">
                <label class="form-label">Name</label>
                <input v-model="profile.name" class="form-control">
              </div>
              <div class="mb-3">
                <label class="form-label">New Password <small class="text-muted">(leave blank to keep)</small></label>
                <input v-model="profile.password" type="password" class="form-control" placeholder="••••••">
              </div>
              <button class="btn btn-success" @click="saveProfile">Save Changes</button>
            </div>
          </div>
        </div>
      </div>
    </div>`,
};
