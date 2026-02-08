// Login.js
const loginUser = async () => {
  const res = await fetch("https://pixelhub-backend.onrender.com/api/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const data = await res.json();

  if (res.ok) {
    localStorage.setItem("token", data.access_token);
    navigate("/wallpapers");
  } else {
    alert(data.error);
  }
};
