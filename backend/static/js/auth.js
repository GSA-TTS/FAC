import { UserManager, WebStorageStateStore } from 'oidc-client-ts';
import crypto from 'crypto-js';
import { queryAPI } from '/static/compiled/js/api';

/* eslint-disable-next-line no-undef */
const appBaseUrl = typeof baseUrl !== 'undefined' ? baseUrl : '/';
const fullBaseUrl = window.location.origin + appBaseUrl;

const settings = {
  authority: 'https://idp.int.identitysandbox.gov',
  client_id: 'urn:gov:gsa:openidconnect.profiles:sp:sso:gsa:gsa-fac-pkce-01',
  redirect_uri: fullBaseUrl + 'auth/post-login', // baseUrl is set in a script tag right before this script loads
  post_logout_redirect_uri: fullBaseUrl + '?logout=success',
  response_type: 'code',
  scope: 'openid email roles all_emails',
  end_session_endpoint: 'http://fac-dev.app.cloud.gov/api/auth/token',
  response_mode: 'query',

  automaticSilentRenew: false,
  filterProtocolClaims: true,
  acr_values: 'http://idmanagement.gov/ns/assurance/ial/1',
};

const userManager = new UserManager(settings);

const tokenStore = new WebStorageStateStore();

export const getApiToken = () => {
  return tokenStore.get('fac-api-token');
};

(function () {
  function attachSignInButtonHandler() {
    const signInButtons = document.getElementsByClassName('sign-in-button');
    Array.prototype.forEach.call(signInButtons, (signInButton) => {
      signInButton.addEventListener('click', () => {
        const nonce = crypto.lib.WordArray.random(32).toString(
          crypto.enc.Base64
        );

        userManager.signinRedirect({
          state: {
            some: 'data',
          },
          nonce,
        });
      });
    });
  }

  function handleLogoutSuccess() {
    sessionStorage.clear();
    localStorage.removeItem('oidc.fac-api-token');
    window.location = settings.post_logout_redirect_uri;
  }

  function handleLogoutError(e) {
    console.error(e);
  }

  function logout() {
    queryAPI(
      '/api/auth/token',
      {},
      {
        method: 'DELETE',
      },
      [handleLogoutSuccess, handleLogoutError]
    );
  }

  function getUserInfo() {
    const userInfoCtr = document.getElementById('user-info');
    userManager.getUser().then((user) => {
      if (user) {
        userInfoCtr.innerText = user.profile.email;
        const params = new URLSearchParams(window.location.search);
        if (params.has('reportId')) {
          checkAccessToAudit(params.get('reportId'));
        }
      }
    });
  }

  function checkAccessToAudit(reportId) {
    queryAPI('/access-list', undefined, { method: 'GET' }, [
      function (audits) {
        if (hasAccessToAudit(audits, reportId)) return;
        window.location = fullBaseUrl + `?authorized=false`;
      },
      function (data) {
        console.error(data);
      },
    ]);
  }

  function attachEventHandlers() {
    attachSignInButtonHandler();

    const postLoginRedirect = document.getElementById('post-login-redirect');
    if (postLoginRedirect) {
      userManager.signinRedirectCallback().then(function (userInfo) {
        const headers = new Headers();
        headers.append('Authorization', 'Bearer ' + userInfo.id_token);

        const ENDPOINT = 'https://fac-dev.app.cloud.gov/api/auth/token';
        //const ENDPOINT = 'http://localhost:8000/api/auth/token';

        // exchange the login.gov JWT for the FAC API token
        fetch(ENDPOINT, {
          method: 'POST',
          headers: headers,
        })
          .then((resp) => resp.json())
          .then((data) => tokenStore.set('fac-api-token', data.token))
          .then(() => (window.location = appBaseUrl + 'audit/new/step-1'));
      });
    }

    const signOutBtn = document.querySelector('.sign-out button');
    if (signOutBtn) {
      signOutBtn.addEventListener('click', (e) => {
        e.preventDefault();
        logout();
      });
    }

    window.addEventListener('load', () => {
      getUserInfo();
      checkLogin();
    });
  }

  function getUserAuditIds(audits) {
    const auditIds = new Set(audits.map((a) => a.report_id));
    return auditIds;
  }

  function hasAccessToAudit(audits, id) {
    const auditIds = getUserAuditIds(audits);
    return auditIds.has(id);
  }

  function checkLogin() {
    // `runningInCi` is an environment variable
    // eslint-disable-next-line no-undef
    if (runningInCi) {
      document.body.classList.remove('no-js');
      return;
    }

    const path = window.location.pathname;
    if (path == appBaseUrl || path.match('auth')) return;

    userManager
      .getUser()
      .then((user) => {
        if (user) {
          document.body.classList.remove('no-js');
        } else {
          window.location = fullBaseUrl + `?authorized=false`;
        }
      })
      .catch((e) => {
        console.error(e);
      });
  }

  function init() {
    attachEventHandlers();
  }

  init();
})();
