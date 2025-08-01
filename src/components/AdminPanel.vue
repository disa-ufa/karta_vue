<template>
  <div class="admin-panel">
    <h2>Админ-панель</h2>
    <div v-if="!isLoggedIn" class="login-form">
      <input v-model="login" placeholder="Логин" />
      <input v-model="password" type="password" placeholder="Пароль" />
      <button @click="loginAdmin">Войти</button>
      <div v-if="error" class="error">{{ error }}</div>
    </div>
    <div v-else>
      <button class="logout-btn" @click="logout">Выйти</button>
      <h3>Заявки на регистрацию</h3>
      <table v-if="requests.length" class="requests-table">
        <thead>
          <tr>
            <th>Организация</th>
            <th>Министерство</th>
            <th>Контактное лицо</th>
            <th>Телефон</th>
            <th>Email</th>
            <th>Пароль (hash)</th>
            <th>Статус</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="req in requests" :key="req._id">
            <td><b>{{ req.orgName }}</b></td>
            <td>{{ req.ministry }}</td>
            <td>{{ req.contactName }}</td>
            <td>{{ req.contactPhone }}</td>
            <td>{{ req.email }}</td>
            <td style="font-size:11px; color:#555;">{{ req.passwordHash }}</td>
            <td>
              <span :style="{ color: statusColor(req.status) }">{{ req.status }}</span>
            </td>
            <td>
              <button v-if="req.status==='pending'" class="approve-btn" @click="approve(req._id)">✅</button>
              <button v-if="req.status==='pending'" class="reject-btn" @click="reject(req._id)">❌</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="no-requests">Нет заявок</div>
    </div>
  </div>
</template>

<script>
const API_URL = import.meta.env.VITE_API_URL || "http://136.169.171.150:8888";

export default {
  data() {
    return {
      login: "",
      password: "",
      isLoggedIn: false,
      error: "",
      requests: [],
      token: "",
    };
  },
  methods: {
    async loginAdmin() {
      this.error = "";
      try {
        const res = await fetch(`${API_URL}/api/admin/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ login: this.login, password: this.password }),
        });
        const data = await res.json();
        if (res.ok) {
          this.isLoggedIn = true;
          this.token = data.token;
          this.fetchRequests();
        } else {
          this.error = data.error || "Ошибка входа";
        }
      } catch {
        this.error = "Нет соединения с сервером";
      }
    },
    async fetchRequests() {
      try {
        const res = await fetch(`${API_URL}/api/admin/registration-requests`, {
          headers: { Authorization: `Bearer ${this.token}` },
        });
        if (!res.ok) throw new Error("Ошибка загрузки заявок");
        this.requests = await res.json();
      } catch {
        this.error = "Ошибка получения заявок";
      }
    },
    async approve(id) {
      try {
        await fetch(`${API_URL}/api/admin/registration-request/${id}/approve`, {
          method: "PATCH",
          headers: { Authorization: `Bearer ${this.token}` },
        });
        this.fetchRequests();
      } catch {
        this.error = "Ошибка подтверждения";
      }
    },
    async reject(id) {
      try {
        await fetch(`${API_URL}/api/admin/registration-request/${id}/reject`, {
          method: "PATCH",
          headers: { Authorization: `Bearer ${this.token}` },
        });
        this.fetchRequests();
      } catch {
        this.error = "Ошибка отклонения";
      }
    },
    statusColor(status) {
      return status === "approved"
        ? "green"
        : status === "rejected"
        ? "red"
        : "gray";
    },
    logout() {
      this.isLoggedIn = false;
      this.token = "";
      this.requests = [];
    },
  },
};
</script>

<style scoped>
.profile-form-outer {
  overflow-y: auto;
  height: 100vh; /* важно для появления полосы прокрутки */
}
.admin-panel {
  max-width: 1100px;
  margin: 32px auto 0 auto;
  padding: 18px 20px 40px 20px;
  background: #fafbfc;
  border-radius: 12px;
  box-shadow: 0 4px 16px #0001;
  font-family: "Segoe UI", "Arial", sans-serif;
}
h2 {
  margin-bottom: 16px;
}
.logout-btn {
  background: #eee;
  border: none;
  padding: 6px 14px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 15px;
  margin-bottom: 15px;
}
.login-form input {
  margin: 0 8px 8px 0;
  padding: 6px;
  border-radius: 4px;
  border: 1px solid #bbb;
}
.login-form button {
  padding: 6px 14px;
  border-radius: 4px;
  border: none;
  background: #359;
  color: #fff;
  cursor: pointer;
}
.error {
  color: #e55;
  margin-top: 7px;
}
.requests-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 18px;
  background: #fff;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 2px 6px #0002;
}
.requests-table th,
.requests-table td {
  border: 1px solid #eaeaea;
  padding: 7px 10px;
  text-align: left;
}
.requests-table th {
  background: #f0f3f7;
  font-weight: 600;
}
.approve-btn, .reject-btn {
  font-size: 18px;
  margin: 0 3px;
  padding: 3px 7px;
  border: 1px solid #bbb;
  border-radius: 4px;
  cursor: pointer;
}
.approve-btn { background: #d7f9d7; }
.reject-btn { background: #ffd5d5; }
.no-requests {
  text-align: center;
  margin-top: 24px;
  color: #666;
  font-size: 18px;
}
</style>
