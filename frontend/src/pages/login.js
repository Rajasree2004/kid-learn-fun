import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  // ✅ Handle Manual Login (Email & Password)
  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const response = await fetch("http://localhost:8000/api/auth/login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || "Login failed");
        return;
      }

      // ✅ Store JWT Token in localStorage
      localStorage.setItem("auth_token", data.access_token);
      navigate("/dashboard");
    } catch (err) {
      setError("Something went wrong. Try again.");
    }
  };

  // ✅ Handle Google Login via Auth0
  const handleGoogleLogin = () => {
    window.location.href = "http://localhost:8000/api/auth/login/google/";
  };

  return (
    <div>
      <h2>Login</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      
      {/* ✅ Manual Login Form */}
      <form onSubmit={handleLogin}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit">Login</button>
      </form>

      {/* ✅ Google Login Button */}
      <button onClick={handleGoogleLogin} style={{ marginTop: "10px", background: "red", color: "white" }}>
        Login with Google
      </button>

      <p>Don't have an account? <a href="/register">Register</a></p>
    </div>
  );
};

export default Login;
