(function () {
    'use strict';

    angular
        .module('ivigilate.authentication.services')
        .factory('AuthInterceptor', AuthInterceptor);

    AuthInterceptor.$inject = ['$cookieStore', '$q'];

    function AuthInterceptor($cookieStore, $q) {

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
                $location.path('/login');
            }
            return $q.reject(rejection);
        }
    }
})();