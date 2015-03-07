(function () {
    'use strict';

    angular
        .module('ivigilate.authentication.controllers')
        .controller('LoginController', LoginController);

    LoginController.$inject = ['$location', '$scope', 'Authentication'];

    function LoginController($location, $scope, Authentication) {
        var vm = this;
        vm.login = login;

        activate();

        function activate() {
            // If the user is authenticated, they should not be here.
            if (Authentication.isAuthenticated()) {
                $location.url('/');
            }
        }

        function login() {
            Authentication.login(vm.email, vm.password).then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                Authentication.setAuthenticatedUser(data.data);
                window.location = '/'; //use this instead of $location.url to force refresh the navbar
            }

            function errorFn(data, status, headers, config) {
                vm.error = 'Failed to login user with error: ' + JSON.stringify(data.data.message);
            }
        }
    }
})();