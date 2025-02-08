import React from "react";
import ReactDOM from "react-dom/client";
import AppRouter from "./router";
// import AuthProvider from "./auth";
import { Auth0Provider } from "@auth0/auth0-react";


const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
      <AppRouter />
  </React.StrictMode>
);
