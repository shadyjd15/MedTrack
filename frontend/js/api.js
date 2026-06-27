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

  listPrescriptions: () => apiRequest("/prescriptions"),
  getPrescription: (id) => apiRequest(`/prescriptions/${id}`),
  createPrescription: (formData) => apiRequest("/prescriptions", { method: "POST", body: formData, isForm: true }),
  updatePrescription: (id, payload) => apiRequest(`/prescriptions/${id}`, { method: "PUT", body: payload }),
  deletePrescription: (id) => apiRequest(`/prescriptions/${id}`, { method: "DELETE" }),

  listMedicines: (params = {}) => {
    const qs = new URLSearchParams(Object.entries(params).filter(([, v]) => v !== "" && v != null)).toString();
    return apiRequest(`/medicines${qs ? `?${qs}` : ""}`);
  },
  createMedicine: (formData) => apiRequest("/medicines", { method: "POST", body: formData, isForm: true }),
  updateMedicine: (id, payload) => apiRequest(`/medicines/${id}`, { method: "PUT", body: payload }),
  deleteMedicine: (id) => apiRequest(`/medicines/${id}`, { method: "DELETE" }),
  uploadMedicinePhoto: (id, formData) => apiRequest(`/medicines/${id}/photo`, { method: "POST", body: formData, isForm: true }),
  findByComposition: (composition) => apiRequest(`/medicines/by-composition/${encodeURIComponent(composition)}`),

  listTags: (q = "") => apiRequest(`/tags${q ? `?q=${encodeURIComponent(q)}` : ""}`),

  dashboardStats: () => apiRequest("/dashboard/stats"),
};

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
