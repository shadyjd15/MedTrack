const API_BASE = "/api";

const Auth = {
  getToken() { return localStorage.getItem("mt_token"); },
  getUser() {
    try { return JSON.parse(localStorage.getItem("mt_user") || "null"); } catch { return null; }
  },
  setSession(token, user) {
    localStorage.setItem("mt_token", token);
    localStorage.setItem("mt_user", JSON.stringify(user));
  },
  clear() {
    localStorage.removeItem("mt_token");
    localStorage.removeItem("mt_user");
  },
  isAdmin() {
    const u = this.getUser();
    return u && u.role === "admin";
  },
  requireAuth() {
    if (!this.getToken()) {
      window.location.href = "/index.html";
    }
  },
  logout() {
    this.clear();
    window.location.href = "/index.html";
  }
};

async function apiRequest(path, { method = "GET", body = null, isForm = false } = {}) {
  const headers = {};
  const token = Auth.getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (!isForm && body) headers["Content-Type"] = "application/json";

  const user = Auth.getUser();
  if (user && user.role === "caregiver") {
    const activePatient = localStorage.getItem("mt_active_patient");
    if (activePatient) headers["X-Patient-Id"] = activePatient;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: isForm ? body : (body ? JSON.stringify(body) : undefined),
  });

  if (res.status === 401) {
    Auth.clear();
    window.location.href = "/index.html";
    throw new Error("Unauthorized");
  }

  let data = null;
  try { data = await res.json(); } catch { /* no body */ }

  if (!res.ok) {
    const msg = (data && data.detail) ? data.detail : `Request failed (${res.status})`;
    throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
  }
  return data;
}

const Api = {
  login: (username, password) => apiRequest("/auth/login", { method: "POST", body: { username, password } }),
  me: () => apiRequest("/auth/me"),

  listUsers: () => apiRequest("/users"),
  createUser: (payload) => apiRequest("/users", { method: "POST", body: payload }),
  updateUser: (id, payload) => apiRequest(`/users/${id}`, { method: "PUT", body: payload }),
  deleteUser: (id) => apiRequest(`/users/${id}`, { method: "DELETE" }),
  changeMyPassword: (password) => apiRequest("/users/me/password", { method: "PUT", body: { password } }),
  updateMyTheme: (theme_preference) => apiRequest("/users/me/theme", { method: "PUT", body: { theme_preference } }),
  updateMyCurrency: (currency) => apiRequest("/users/me/currency", { method: "PUT", body: { currency } }),

  listPrescriptions: () => apiRequest("/prescriptions"),
  getPrescription: (id) => apiRequest(`/prescriptions/${id}`),
  createPrescription: (formData) => apiRequest("/prescriptions", { method: "POST", body: formData, isForm: true }),
  updatePrescription: (id, payload) => apiRequest(`/prescriptions/${id}`, { method: "PUT", body: payload }),
  deletePrescription: (id) => apiRequest(`/prescriptions/${id}`, { method: "DELETE" }),
  addCostItem: (prescId, payload) => apiRequest(`/prescriptions/${prescId}/cost-items`, { method: "POST", body: payload }),
  deleteCostItem: (prescId, itemId) => apiRequest(`/prescriptions/${prescId}/cost-items/${itemId}`, { method: "DELETE" }),

  listMedicines: (params = {}) => {
    const qs = new URLSearchParams(Object.entries(params).filter(([, v]) => v !== "" && v != null)).toString();
    return apiRequest(`/medicines${qs ? `?${qs}` : ""}`);
  },
  createMedicine: (formData) => apiRequest("/medicines", { method: "POST", body: formData, isForm: true }),
  updateMedicine: (id, payload) => apiRequest(`/medicines/${id}`, { method: "PUT", body: payload }),
  deleteMedicine: (id) => apiRequest(`/medicines/${id}`, { method: "DELETE" }),
  uploadMedicinePhoto: (id, formData) => apiRequest(`/medicines/${id}/photo`, { method: "POST", body: formData, isForm: true }),
  findByComposition: (composition) => apiRequest(`/medicines/by-composition/${encodeURIComponent(composition)}`),
  adjustRefill: (id, payload) => apiRequest(`/medicines/${id}/refill`, { method: "POST", body: payload }),

  listTags: (q = "") => apiRequest(`/tags${q ? `?q=${encodeURIComponent(q)}` : ""}`),

  dashboardStats: () => apiRequest("/dashboard/stats"),

  listLabTests: () => apiRequest("/lab-tests"),
  createLabTest: (formData) => apiRequest("/lab-tests", { method: "POST", body: formData, isForm: true }),
  updateLabTest: (id, payload) => apiRequest(`/lab-tests/${id}`, { method: "PUT", body: payload }),
  uploadLabTestFile: (id, formData) => apiRequest(`/lab-tests/${id}/file`, { method: "POST", body: formData, isForm: true }),
  deleteLabTest: (id) => apiRequest(`/lab-tests/${id}`, { method: "DELETE" }),

  listVaccinations: () => apiRequest("/vaccinations"),
  createVaccination: (payload) => apiRequest("/vaccinations", { method: "POST", body: payload }),
  updateVaccination: (id, payload) => apiRequest(`/vaccinations/${id}`, { method: "PUT", body: payload }),
  uploadVaccinationCert: (id, formData) => apiRequest(`/vaccinations/${id}/certificate`, { method: "POST", body: formData, isForm: true }),
  deleteVaccination: (id) => apiRequest(`/vaccinations/${id}`, { method: "DELETE" }),

  ocrScan: (formData) => apiRequest("/ocr/scan", { method: "POST", body: formData, isForm: true }),

  getVersion: () => apiRequest("/version"),

  listAllergies: () => apiRequest("/allergies"),
  createAllergy: (payload) => apiRequest("/allergies", { method: "POST", body: payload }),
  updateAllergy: (id, payload) => apiRequest(`/allergies/${id}`, { method: "PUT", body: payload }),
  deleteAllergy: (id) => apiRequest(`/allergies/${id}`, { method: "DELETE" }),
  checkAllergy: (composition) => apiRequest(`/medicines/allergy-check?composition=${encodeURIComponent(composition)}`),

  listCaregiverLinks: () => apiRequest("/caregivers/links"),
  createCaregiverLink: (payload) => apiRequest("/caregivers/links", { method: "POST", body: payload }),
  deleteCaregiverLink: (id) => apiRequest(`/caregivers/links/${id}`, { method: "DELETE" }),
  myPatients: () => apiRequest("/caregivers/my-patients"),

  getEmailSettings: () => apiRequest("/email-settings"),
  updateEmailSettings: (payload) => apiRequest("/email-settings", { method: "PUT", body: payload }),
  sendTestEmail: (to) => apiRequest("/email-settings/test", { method: "POST", body: { to } }),

  importMedicinesCsv: (formData) => apiRequest("/medicines/import", { method: "POST", body: formData, isForm: true }),
};

const CURRENCY_SYMBOLS = {
  USD: "$", EUR: "€", GBP: "£", SAR: "ر.س", AED: "د.إ", EGP: "E£",
  INR: "₹", PKR: "₨", CAD: "CA$", AUD: "A$", JPY: "¥",
};

function currencySymbol(code) {
  return CURRENCY_SYMBOLS[code] || (code ? code + " " : "$");
}

function money(amount, currencyCode) {
  const code = currencyCode || (Auth.getUser() && Auth.getUser().currency) || "USD";
  return `${currencySymbol(code)}${(amount || 0).toFixed(2)}`;
}

function exportUrl(path, params = {}) {
  const qs = new URLSearchParams(Object.entries(params).filter(([, v]) => v !== "" && v != null)).toString();
  return `${API_BASE}/export/${path}${qs ? `?${qs}` : ""}`;
}

async function downloadMedicineTemplate() {
  const token = Auth.getToken();
  const res = await fetch(`${API_BASE}/medicines/import/template`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) { showToast("Could not download template", "error"); return; }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "medicine-import-template.csv";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

async function downloadExport(path, params = {}) {
  const token = Auth.getToken();
  const headers = { Authorization: `Bearer ${token}` };
  const user = Auth.getUser();
  if (user && user.role === "caregiver") {
    const activePatient = localStorage.getItem("mt_active_patient");
    if (activePatient) headers["X-Patient-Id"] = activePatient;
  }
  const res = await fetch(exportUrl(path, params), { headers });
  if (!res.ok) { showToast("Export failed", "error"); return; }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = path.replace(".csv", "").replace(".pdf", "") + (path.includes(".csv") ? ".csv" : ".pdf");
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

function showToast(message, type = "default") {
  let stack = document.querySelector(".toast-stack");
  if (!stack) {
    stack = document.createElement("div");
    stack.className = "toast-stack";
    document.body.appendChild(stack);
  }
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.textContent = message;
  stack.appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

function fmtDate(d) {
  if (!d) return "—";
  const dt = new Date(d);
  return dt.toLocaleDateString(undefined, { day: "2-digit", month: "short", year: "numeric" });
}

function initials(name) {
  if (!name) return "?";
  return name.split(" ").filter(Boolean).slice(0, 2).map(s => s[0].toUpperCase()).join("");
}
