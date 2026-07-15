const StaffDashboard = {
    data() {
        return {
            tab: "treks",
            stats: {},
            treks: [],
            error: "",
            showSlotsModal: false,
            slotsForm: { id: null, name: "", total_slots: 0 },
            showParticipants: false,
            currentTrek: null,
            participants: [],
            analytics: null,
            charts: [],
        };
    },
    computed: { auth: () => auth },
    beforeUnmount() { this.charts.forEach(c => c.destroy()); },
    methods: {
        switchTab(t) {
            this.tab = t;
            if (t === "analytics") this.loadAnalytics();
        },
        async loadAnalytics() {
            this.analytics = (await axios.get("/api/staff/analytics")).data;
            this.$nextTick(() => this.renderCharts());
        },
        renderCharts() {
            this.charts.forEach(c => c.destroy());
            this.charts = [
                TMACharts.popularTreks(this.$refs.sPopular, this.analytics),
                TMACharts.monthlyTrend(this.$refs.sTrend, this.analytics),
                TMACharts.statusBreakdown(this.$refs.sStatus, this.analytics),
            ];
        },
        async loadAll() {
            this.stats = (await axios.get("/api/staff/stats")).data;
            this.treks = (await axios.get("/api/staff/treks")).data;
        },
        openSlots(t) {
            this.slotsForm = { id: t.id, name: t.name, total_slots: t.total_slots };
            this.error = "";
            this.showSlotsModal = true;
        },
        async saveSlots() {
            this.error = "";
            try {
                await axios.patch(`/api/staff/treks/${this.slotsForm.id}/slots`, {
                    total_slots: this.slotsForm.total_slots,
                });
                this.showSlotsModal = false;
                this.loadAll();
            } catch (e) {
                this.error = e.response?.data?.error || "Could not update slots.";
            }
        },
        async changeStatus(t, status) {
            try {
                await axios.patch(`/api/staff/treks/${t.id}/status`, { status });
                this.loadAll();
            } catch (e) {
                alert(e.response?.data?.error || "Could not update status.");
            }
        },
        async openParticipants(t) {
            this.currentTrek = t;
            this.participants = (await axios.get(`/api/staff/treks/${t.id}/participants`)).data;
            this.showParticipants = true;
        },
        async setParticipantStatus(p, status) {
            try {
                const { data } = await axios.patch(`/api/staff/bookings/${p.booking_id}/status`, { status });
                p.status = data.status;
                this.loadAll();
            } catch (e) {
                alert(e.response?.data?.error || "Could not update participant.");
            }
        },
    },
    mounted() { this.loadAll(); },
    template: `
    <div>
      <h3 class="text-success mb-3">Trek Staff Dashboard</h3>

      <div class="row g-3 mb-4">
        <div class="col-4" v-for="c in [
              {label:'Assigned Treks', val:stats.assigned_treks, cls:'text-success'},
              {label:'Registered Trekkers', val:stats.total_registered, cls:'text-primary'},
              {label:'Open Treks', val:stats.open_treks, cls:'text-warning'}]" :key="c.label">
          <div class="card shadow-sm text-center">
            <div class="card-body">
              <div class="display-6" :class="c.cls">{{ c.val ?? 0 }}</div>
              <div class="text-muted">{{ c.label }}</div>
            </div>
          </div>
        </div>
      </div>

      <ul class="nav nav-tabs mb-3">
        <li class="nav-item">
          <a class="nav-link" :class="{active: tab==='treks'}" href="#" @click.prevent="switchTab('treks')">My Treks</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{active: tab==='analytics'}" href="#" @click.prevent="switchTab('analytics')">Analytics</a>
        </li>
      </ul>

      <div v-if="tab==='treks'" class="table-responsive">
        <table class="table table-striped align-middle">
          <thead><tr>
            <th>ID</th><th>Name</th><th>Location</th><th>Slots</th>
            <th>Registered</th><th>Status</th><th style="min-width:230px">Actions</th>
          </tr></thead>
          <tbody>
            <tr v-for="t in treks" :key="t.id">
              <td>{{ t.id }}</td><td>{{ t.name }}</td><td>{{ t.location }}</td>
              <td>{{ t.available_slots }}/{{ t.total_slots }}</td>
              <td>{{ t.registered_count }}</td>
              <td>
                <select class="form-select form-select-sm" :value="t.status"
                        @change="changeStatus(t, $event.target.value)">
                  <option>Open</option><option>Closed</option><option>Completed</option>
                  <option v-if="!['Open','Closed','Completed'].includes(t.status)" :value="t.status" disabled>
                    {{ t.status }}
                  </option>
                </select>
              </td>
              <td class="text-nowrap">
                <button class="btn btn-sm btn-outline-primary me-1" @click="openSlots(t)">Slots</button>
                <button class="btn btn-sm btn-outline-secondary" @click="openParticipants(t)">Participants</button>
              </td>
            </tr>
            <tr v-if="!treks.length"><td colspan="7" class="text-center text-muted">No treks assigned to you yet.</td></tr>
          </tbody>
        </table>
      </div>

      <div v-if="tab==='analytics'">
        <div v-if="analytics" class="row g-3">
          <div class="col-lg-8">
            <div class="card shadow-sm h-100"><div class="card-body">
              <h6 class="text-muted mb-3">Participation — My Treks</h6>
              <div style="height:300px"><canvas ref="sPopular"></canvas></div>
            </div></div>
          </div>
          <div class="col-lg-4">
            <div class="card shadow-sm h-100"><div class="card-body">
              <h6 class="text-muted mb-3">Booking Status</h6>
              <div style="height:300px"><canvas ref="sStatus"></canvas></div>
            </div></div>
          </div>
          <div class="col-12">
            <div class="card shadow-sm"><div class="card-body">
              <h6 class="text-muted mb-3">Monthly Participation (last 6 months)</h6>
              <div style="height:280px"><canvas ref="sTrend"></canvas></div>
            </div></div>
          </div>
        </div>
        <div v-else class="text-muted text-center py-4">Loading analytics…</div>
      </div>

      <div v-if="showSlotsModal" class="tma-modal-backdrop" @click.self="showSlotsModal=false">
        <div class="card tma-modal" style="max-width:420px">
          <div class="card-body">
            <h5 class="text-success">Update Capacity — {{ slotsForm.name }}</h5>
            <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
            <label class="form-label">Total Slots (capacity)</label>
            <input type="number" min="1" v-model.number="slotsForm.total_slots" class="form-control">
            <div class="form-text">Available seats are recalculated from current bookings.</div>
            <div class="mt-3 text-end">
              <button class="btn btn-secondary me-2" @click="showSlotsModal=false">Cancel</button>
              <button class="btn btn-success" @click="saveSlots">Save</button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="showParticipants" class="tma-modal-backdrop" @click.self="showParticipants=false">
        <div class="card tma-modal">
          <div class="card-body">
            <h5 class="text-success">Participants — {{ currentTrek?.name }}</h5>
            <div class="table-responsive">
              <table class="table table-sm align-middle">
                <thead><tr><th>Name</th><th>Email</th><th>Status</th><th>Actions</th></tr></thead>
                <tbody>
                  <tr v-for="p in participants" :key="p.booking_id">
                    <td>{{ p.user_name }}</td><td>{{ p.user_email }}</td>
                    <td><span class="badge bg-secondary">{{ p.status }}</span></td>
                    <td class="text-nowrap">
                      <button class="btn btn-sm btn-outline-success me-1"
                              :disabled="p.status==='Completed'"
                              @click="setParticipantStatus(p,'Completed')">Complete</button>
                      <button class="btn btn-sm btn-outline-danger"
                              :disabled="p.status==='Cancelled'"
                              @click="setParticipantStatus(p,'Cancelled')">Cancel</button>
                    </td>
                  </tr>
                  <tr v-if="!participants.length"><td colspan="4" class="text-center text-muted">No participants.</td></tr>
                </tbody>
              </table>
            </div>
            <div class="text-end"><button class="btn btn-secondary" @click="showParticipants=false">Close</button></div>
          </div>
        </div>
      </div>
    </div>`,
};
