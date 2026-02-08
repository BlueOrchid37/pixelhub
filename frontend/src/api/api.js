// api/api.js
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
