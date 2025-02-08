import React, { useEffect, useState } from "react";

const Login = () => {
  const [user, setUser] = useState(null);

  const login = async () => {
    window.location.href = "http://localhost:8000/api/auth/login/"; // Django handles Auth0 login
  };

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const token = localStorage.getItem("auth_token");
        if (!token) return;

        const response = await fetch("http://localhost:8000/api/profile/", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          setUser(data);
        }
      } catch (error) {
        console.error("Error fetching user:", error);
      }
    };

    fetchUser();
  }, []);

  return (
    <div>
      {user ? (
        <h1>Welcome, {user.username}!</h1>
      ) : (
        <button onClick={login}>Login with Auth0</button>
      )}
    </div>
  );
};

export default Login;
