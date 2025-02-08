import { createAuth0Client } from "@auth0/auth0-spa-js";

const auth0 = await createAuth0Client({
  domain: process.env.REACT_APP_AUTH0_DOMAIN,
  clientId: process.env.REACT_APP_AUTH0_CLIENT_ID,
  authorizationParams: {
    redirect_uri: window.location.origin,
  }
});

export default auth0;
