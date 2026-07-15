const AdminDashboard = {
    data() {
        return {
            tab: "overview",
            stats: {},
            treks: [], staff: [], users: [], bookings: [],
            trekSearch: "", staffSearch: "", userSearch: "",
            bookingStatus: "", bookingSearch: "",
            error: "",
            // Trek modal
            showTrekModal: false,
            trekForm: {},
            trekEditing: false,
            // Staff modal
            showStaffModal: false,
            staffForm: {},
            // Analytics
            analytics: null,
            charts: [],
        };
    },
    computed: { auth: () => auth },
    methods: {
        async loadStats() {
            this.stats = (await axios.get("/api/admin/stats")).data;
        },
        async loadTreks() {
            this.treks = (await axios.get("/api/admin/treks", { params: { q: this.trekSearch } })).data;
        },
        async loadStaff() {
            this.staff = (await axios.get("/api/admin/staff", { params: { q: this.staffSearch } })).data;
        },
        async loadUsers() {
            this.users = (await axios.get("/api/admin/users", { params: { q: this.userSearch } })).data;
        },
        async loadBookings() {
            const params = {};
            if (this.bookingStatus) params.status = this.bookingStatus;
            if (this.bookingSearch) params.q = this.bookingSearch;
            this.bookings = (await axios.get("/api/admin/bookings", { params })).data;
        },
        switchTab(t) {
            this.tab = t;
            if (t === "overview") this.loadStats();
            if (t === "treks") { this.loadTreks(); this.loadStaff(); }
            if (t === "staff") this.loadStaff();
            if (t === "users") this.loadUsers();
            if (t === "bookings") this.loadBookings();
            if (t === "analytics") this.loadAnalytics();
        },
        async loadAnalytics() {
            this.analytics = (await axios.get("/api/public/stats")).data;
            this.$nextTick(() => this.renderCharts());
        },
        renderCharts() {
            this.charts.forEach(c => c.destroy());
            this.charts = [
                TMACharts.popularTreks(this.$refs.aPopular, this.analytics),
                TMACharts.monthlyTrend(this.$refs.aTrend, this.analytics),
                TMACharts.statusBreakdown(this.$refs.aStatus, this.analytics),
                TMACharts.difficulty(this.$refs.aDifficulty, this.analytics),
            ];
        },
        // ---- Trek CRUD ----
        newTrek() {
            this.trekEditing = false;
            this.trekForm = {
                name: "", location: "", difficulty: "Easy", duration_days: 1,
                total_slots: 10, status: "Pending", assigned_staff_id: "",
                start_date: "", end_date: "",
            };
            this.error = "";
            this.showTrekModal = true;
        },
        editTrek(t) {
            this.trekEditing = true;
            this.trekForm = {
                id: t.id, name: t.name, location: t.location, difficulty: t.difficulty,
                duration_days: t.duration_days, total_slots: t.total_slots, status: t.status,
                assigned_staff_id: t.assigned_staff_id || "",
                start_date: t.start_date || "", end_date: t.end_date || "",
            };
            this.error = "";
            this.showTrekModal = true;
        },
        async saveTrek() {
            this.error = "";
            try {
                const payload = { ...this.trekForm };
                if (!payload.assigned_staff_id) payload.assigned_staff_id = null;
                if (this.trekEditing) {
                    await axios.put(`/api/admin/treks/${payload.id}`, payload);
                } else {
                    await axios.post("/api/admin/treks", payload);
                }
                this.showTrekModal = false;
                this.loadTreks();
                this.loadStats();
            } catch (e) {
                this.error = e.response?.data?.error || "Could not save trek.";
            }
        },
        async deleteTrek(t) {
            if (!confirm(`Delete trek "${t.name}"? This removes its bookings too.`)) return;
            await axios.delete(`/api/admin/treks/${t.id}`);
            this.loadTreks();
            this.loadStats();
        },
        // ---- Staff ----
        newStaff() {
            this.staffForm = { name: "", email: "", password: "", contact_number: "" };
            this.error = "";
            this.showStaffModal = true;
        },
        async saveStaff() {
            this.error = "";
            try {
                await axios.post("/api/admin/staff", this.staffForm);
                this.showStaffModal = false;
                this.loadStaff();
                this.loadStats();
            } catch (e) {
                this.error = e.response?.data?.error || "Could not create staff.";
            }
        },
        // ---- Users ----
        async toggleUser(u) {
            const { data } = await axios.patch(`/api/admin/users/${u.id}/toggle-active`);
            u.active = data.active;
        },
    },
    mounted() { this.loadStats(); },
    beforeUnmount() { this.charts.forEach(c => c.destroy()); },
    template: `
    <div>
      <h3 class="text-success mb-3">Admin Dashboard</h3>

      <ul class="nav nav-tabs mb-3">
        <li class="nav-item" v-for="t in ['overview','treks','staff','users','bookings','analytics']" :key="t">
          <a class="nav-link" :class="{active: tab===t}" href="#" @click.prevent="switchTab(t)">
            {{ t.charAt(0).toUpperCase() + t.slice(1) }}
          </a>
        </li>
      </ul>

      <!-- OVERVIEW -->
      <div v-if="tab==='overview'" class="row g-3">
        <div class="col-6 col-md-3" v-for="c in [
              {label:'Treks', val:stats.total_treks, cls:'text-success'},
              {label:'Trekkers', val:stats.total_users, cls:'text-primary'},
              {label:'Staff', val:stats.total_staff, cls:'text-warning'},
              {label:'Bookings', val:stats.total_bookings, cls:'text-danger'}]" :key="c.label">
          <div class="card shadow-sm text-center">
            <div class="card-body">
              <div class="display-6" :class="c.cls">{{ c.val ?? 0 }}</div>
              <div class="text-muted">{{ c.label }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- TREKS -->
      <div v-if="tab==='treks'">
        <div class="d-flex mb-3 gap-2">
          <input v-model="trekSearch" @input="loadTreks" class="form-control" placeholder="Search treks by name / location / id">
          <button class="btn btn-success text-nowrap" @click="newTrek">+ New Trek</button>
        </div>
        <div class="table-responsive">
          <table class="table table-striped align-middle">
            <thead><tr>
              <th>ID</th><th>Name</th><th>Location</th><th>Difficulty</th><th>Days</th>
              <th>Slots</th><th>Status</th><th>Staff</th><th></th>
            </tr></thead>
            <tbody>
              <tr v-for="t in treks" :key="t.id">
                <td>{{ t.id }}</td><td>{{ t.name }}</td><td>{{ t.location }}</td>
                <td>{{ t.difficulty }}</td><td>{{ t.duration_days }}</td>
                <td>{{ t.available_slots }}/{{ t.total_slots }}</td>
                <td><span class="badge bg-secondary">{{ t.status }}</span></td>
                <td>{{ t.assigned_staff_name || '—' }}</td>
                <td class="text-nowrap">
                  <button class="btn btn-sm btn-outline-primary me-1" @click="editTrek(t)">Edit</button>
                  <button class="btn btn-sm btn-outline-danger" @click="deleteTrek(t)">Del</button>
                </td>
              </tr>
              <tr v-if="!treks.length"><td colspan="9" class="text-center text-muted">No treks.</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- STAFF -->
      <div v-if="tab==='staff'">
        <div class="d-flex mb-3 gap-2">
          <input v-model="staffSearch" @input="loadStaff" class="form-control" placeholder="Search staff by name / email / id">
          <button class="btn btn-success text-nowrap" @click="newStaff">+ Add Staff</button>
        </div>
        <div class="table-responsive">
          <table class="table table-striped align-middle">
            <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Contact</th><th>Assigned Treks</th><th>Active</th><th></th></tr></thead>
            <tbody>
              <tr v-for="s in staff" :key="s.id">
                <td>{{ s.id }}</td><td>{{ s.name }}</td><td>{{ s.email }}</td>
                <td>{{ s.contact_number || '—' }}</td><td>{{ s.assigned_treks }}</td>
                <td><span class="badge" :class="s.active?'bg-success':'bg-secondary'">{{ s.active?'Yes':'No' }}</span></td>
                <td>
                  <button class="btn btn-sm" :class="s.active?'btn-outline-danger':'btn-outline-success'"
                          @click="toggleUser(s)">{{ s.active?'Deactivate':'Activate' }}</button>
                </td>
              </tr>
              <tr v-if="!staff.length"><td colspan="7" class="text-center text-muted">No staff.</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- USERS -->
      <div v-if="tab==='users'">
        <input v-model="userSearch" @input="loadUsers" class="form-control mb-3" placeholder="Search users by name / email / id">
        <div class="table-responsive">
          <table class="table table-striped align-middle">
            <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Active</th><th></th></tr></thead>
            <tbody>
              <tr v-for="u in users" :key="u.id">
                <td>{{ u.id }}</td><td>{{ u.name }}</td><td>{{ u.email }}</td>
                <td><span class="badge" :class="u.active?'bg-success':'bg-secondary'">{{ u.active?'Active':'Blacklisted' }}</span></td>
                <td>
                  <button class="btn btn-sm" :class="u.active?'btn-outline-danger':'btn-outline-success'"
                          @click="toggleUser(u)">{{ u.active?'Blacklist':'Restore' }}</button>
                </td>
              </tr>
              <tr v-if="!users.length"><td colspan="5" class="text-center text-muted">No users.</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- BOOKINGS -->
      <div v-if="tab==='bookings'">
        <div class="d-flex mb-3 gap-2">
          <input v-model="bookingSearch" @input="loadBookings" class="form-control"
                 placeholder="Search by trekker or trek">
          <select v-model="bookingStatus" @change="loadBookings" class="form-select" style="max-width:200px">
            <option value="">All statuses</option>
            <option>Booked</option><option>Cancelled</option><option>Completed</option>
          </select>
        </div>
        <div class="table-responsive">
          <table class="table table-striped align-middle">
            <thead><tr><th>ID</th><th>Trekker</th><th>Trek</th><th>Status</th><th>Payment</th><th>Date</th></tr></thead>
            <tbody>
              <tr v-for="b in bookings" :key="b.id">
                <td>{{ b.id }}</td><td>{{ b.user_name }}</td><td>{{ b.trek_name }}</td>
                <td><span class="badge bg-secondary">{{ b.status }}</span></td>
                <td>{{ b.payment_status }}</td>
                <td>{{ (b.booking_date||'').slice(0,10) }}</td>
              </tr>
              <tr v-if="!bookings.length"><td colspan="6" class="text-center text-muted">No bookings.</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ANALYTICS -->
      <div v-if="tab==='analytics'">
        <div v-if="analytics" class="row g-3">
          <div class="col-lg-8">
            <div class="card shadow-sm h-100"><div class="card-body">
              <h6 class="text-muted mb-3">Trek Participation — Most Popular Treks</h6>
              <div style="height:300px"><canvas ref="aPopular"></canvas></div>
            </div></div>
          </div>
          <div class="col-lg-4">
            <div class="card shadow-sm h-100"><div class="card-body">
              <h6 class="text-muted mb-3">Booking Status</h6>
              <div style="height:300px"><canvas ref="aStatus"></canvas></div>
            </div></div>
          </div>
          <div class="col-lg-8">
            <div class="card shadow-sm h-100"><div class="card-body">
              <h6 class="text-muted mb-3">Monthly Participation (last 6 months)</h6>
              <div style="height:280px"><canvas ref="aTrend"></canvas></div>
            </div></div>
          </div>
          <div class="col-lg-4">
            <div class="card shadow-sm h-100"><div class="card-body">
              <h6 class="text-muted mb-3">Treks by Difficulty</h6>
              <div style="height:280px"><canvas ref="aDifficulty"></canvas></div>
            </div></div>
          </div>
        </div>
        <div v-else class="text-muted text-center py-4">Loading analytics…</div>
      </div>

      <!-- TREK MODAL -->
      <div v-if="showTrekModal" class="tma-modal-backdrop" @click.self="showTrekModal=false">
        <div class="card tma-modal">
          <div class="card-body">
            <h5 class="text-success">{{ trekEditing ? 'Edit Trek' : 'New Trek' }}</h5>
            <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
            <div class="row g-2">
              <div class="col-12"><label class="form-label">Name</label>
                <input v-model="trekForm.name" class="form-control"></div>
              <div class="col-6"><label class="form-label">Location</label>
                <input v-model="trekForm.location" class="form-control"></div>
              <div class="col-6"><label class="form-label">Difficulty</label>
                <select v-model="trekForm.difficulty" class="form-select">
                  <option>Easy</option><option>Moderate</option><option>Hard</option></select></div>
              <div class="col-6"><label class="form-label">Duration (days)</label>
                <input type="number" min="1" v-model.number="trekForm.duration_days" class="form-control"></div>
              <div class="col-6"><label class="form-label">Total Slots</label>
                <input type="number" min="1" v-model.number="trekForm.total_slots" class="form-control"></div>
              <div class="col-6"><label class="form-label">Status</label>
                <select v-model="trekForm.status" class="form-select">
                  <option>Pending</option><option>Approved</option><option>Open</option>
                  <option>Closed</option><option>Completed</option></select></div>
              <div class="col-6"><label class="form-label">Assign Staff</label>
                <select v-model="trekForm.assigned_staff_id" class="form-select">
                  <option value="">— None —</option>
                  <option v-for="s in staff" :key="s.id" :value="s.id">{{ s.name }}</option></select></div>
              <div class="col-6"><label class="form-label">Start Date</label>
                <input type="date" v-model="trekForm.start_date" class="form-control"></div>
              <div class="col-6"><label class="form-label">End Date</label>
                <input type="date" v-model="trekForm.end_date" class="form-control"></div>
            </div>
            <div class="mt-3 text-end">
              <button class="btn btn-secondary me-2" @click="showTrekModal=false">Cancel</button>
              <button class="btn btn-success" @click="saveTrek">Save</button>
            </div>
          </div>
        </div>
      </div>

      <!-- STAFF MODAL -->
      <div v-if="showStaffModal" class="tma-modal-backdrop" @click.self="showStaffModal=false">
        <div class="card tma-modal">
          <div class="card-body">
            <h5 class="text-success">Add Trek Staff</h5>
            <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
            <div class="mb-2"><label class="form-label">Name</label>
              <input v-model="staffForm.name" class="form-control"></div>
            <div class="mb-2"><label class="form-label">Email</label>
              <input v-model="staffForm.email" type="email" class="form-control"></div>
            <div class="mb-2"><label class="form-label">Password</label>
              <input v-model="staffForm.password" type="password" class="form-control"></div>
            <div class="mb-2"><label class="form-label">Contact Number</label>
              <input v-model="staffForm.contact_number" class="form-control"></div>
            <div class="mt-3 text-end">
              <button class="btn btn-secondary me-2" @click="showStaffModal=false">Cancel</button>
              <button class="btn btn-success" @click="saveStaff">Create</button>
            </div>
          </div>
        </div>
      </div>
    </div>`,
};
