(function () {
    'use strict';

    angular
        .module('ivigilate.authentication.services')
        .factory('AuthInterceptor', AuthInterceptor);

    AuthInterceptor.$inject = ['$cookieStore', '$location', '$q'];

    function AuthInterceptor($cookieStore, $location, $q) {

        var AuthInterceptor = {
            request: request,
            responseError: responseError
        };
        return AuthInterceptor;

        /////////////////////

        function request (config) {

            config.headers = config.headers || {};

            var user = $cookieStore.get('authenticatedUser');
            if (user) {
                config.headers.Authorization = 'Token ' + user.token;
            }

            return config;
        }

        function responseError (rejection) {
            if (rejection.status === 401) {
                $cookieStore.remove('authenticatedUser');
                $location.path('/login');
            }
            return $q.reject(rejection);
        }
    }
})();