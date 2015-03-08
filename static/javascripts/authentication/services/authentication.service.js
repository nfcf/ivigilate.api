(function () {
    'use strict';

    angular
        .module('ivigilate.authentication.services')
        .factory('Authentication', Authentication);

    Authentication.$inject = ['$cookieStore', '$http'];

    function Authentication($cookieStore, $http) {

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
            return $http.post('/api/v1/users/', {company_id: company_id, email: email, password: password});
        }

        function login(email, password) {
            return $http.post('/api/v1/login/', {email: email, password: password});
        }

        function logout() {
            return $http.post('/api/v1/logout/')
                .then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                Authentication.unauthenticate();
                window.location = '/login';
            }

            function errorFn(data, status, headers, config) {
                console.error('Logout failure!');
            }
        }

        function getAuthenticatedUser() {
            if (!$cookieStore.get('authenticatedUser')) {
                return;
            }

            return $cookieStore.get('authenticatedUser');
        }

        function setAuthenticatedUser(user) {
            $cookieStore.put('authenticatedUser', user);
        }

        function isAuthenticated() {
            return !!$cookieStore.get('authenticatedUser');
        }

        function unauthenticate() {
            $cookieStore.remove('authenticatedUser');
        }
    }
})();