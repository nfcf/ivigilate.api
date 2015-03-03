(function () {
  'use strict';

  angular
    .module('ivigilate.authentication.services')
    .factory('Authentication', Authentication);

  Authentication.$inject = ['$cookies', '$http'];

  function Authentication($cookies, $http) {

      var Authentication = {
          getAuthenticatedUser: getAuthenticatedUser,
          isAuthenticated: isAuthenticated,
          login: login,
          logout: logout,
          register: register,
          setAuthenticatedUser: setAuthenticatedUser,
          unauthenticate: unauthenticate
      };
      return Authentication;

      /////////////////////

      function register(company_id, email, password) {
          return $http.post('/api/v1/users/', {
              company_id: company_id,
              email: email,
              password: password
          }).then(registerSuccessFn, registerErrorFn);

          function registerSuccessFn(data, status, headers, config) {
              Authentication.login(email, password);
          }

          function registerErrorFn(data, status, headers, config) {
              console.error(data.data.status + ": " + data.data.message);
              alert(data.data.status + ": " + data.data.message);
          }
      }

      function login(email, password) {
          return $http.post('/api/v1/login/', {
              email: email, password: password
          }).then(loginSuccessFn, loginErrorFn);

          function loginSuccessFn(data, status, headers, config) {
              Authentication.setAuthenticatedUser(data.data);
              window.location = '/';
          }

          function loginErrorFn(data, status, headers, config) {
              console.error('Login failure!');
          }
      }

      function logout() {
        return $http.post('/api/v1/logout/')
            .then(logoutSuccessFn, logoutErrorFn);

        function logoutSuccessFn(data, status, headers, config) {
            Authentication.unauthenticate();
            window.location = '/';
        }

        function logoutErrorFn(data, status, headers, config) {
            console.error('Logout failure!');
        }
      }

      function getAuthenticatedUser() {
          if (!$cookies.authenticatedUser) {
              return;
          }

          return JSON.parse($cookies.authenticatedUser);
      }

      function setAuthenticatedUser(user) {
          $cookies.authenticatedUser = JSON.stringify(user);
      }

      function isAuthenticated() {
          return !!$cookies.authenticatedUser;
      }

      function unauthenticate() {
          delete $cookies.authenticatedUser;
      }
  }
})();