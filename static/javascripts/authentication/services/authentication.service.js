(function () {
    'use strict';

    angular
        .module('ivigilate.authentication.services')
        .factory('Authentication', Authentication);

    Authentication.$inject = ['$cookieStore', '$http', '$rootScope'];

    function Authentication($cookieStore, $http, $rootScope) {

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
            return $http.post('/api/v1/logout/');
        }

        function getAuthenticatedUser() {
            if (!$cookieStore.get('authenticatedUser')) {
                return;
            }

            return $cookieStore.get('authenticatedUser');
        }

        function setAuthenticatedUser(user) {
            $cookieStore.put('authenticatedUser', user);
            $rootScope.$broadcast('IS_AUTHENTICATED', true);
        }

        function isAuthenticated() {
            $rootScope.$broadcast('IS_AUTHENTICATED', !!$cookieStore.get('authenticatedUser'));
            return !!$cookieStore.get('authenticatedUser');
        }

        function unauthenticate() {
            $cookieStore.remove('authenticatedUser');
            $rootScope.$broadcast('IS_AUTHENTICATED', false);
        }
    }
})();