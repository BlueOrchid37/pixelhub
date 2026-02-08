const API = "https://skilltrack-backend.onrender.com/api";

export const fetchWallpapers = (account) =>
  fetch(`${API}/wallpapers?account=${account}`).then(res => res.json());

export const loginUser = (data) =>
  fetch(`${API}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  }).then(res => res.json());



// services/api.js
const API_BASE = "https://pixelhub-backend.onrender.com";

export const apiFetch = (url, options = {}) => {
  const token = localStorage.getItem("token");

  return fetch(API_BASE + url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  });
};
