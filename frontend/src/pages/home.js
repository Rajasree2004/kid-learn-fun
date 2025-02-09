import React from "react";
import { Link } from "react-router-dom";

const Home = () => {
  return (
    <div>
      <h1>Welcome to Kid Learn Fun</h1>
      <Link to="/register"><button>Go to Login</button></Link>
    </div>
  );
};

export default Home;
