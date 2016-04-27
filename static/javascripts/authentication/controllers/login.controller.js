(function () {
    'use strict';

    angular
        .module('ivigilate.authentication.controllers')
        .controller('LoginController', LoginController);

    LoginController.$inject = ['$location', 'Authentication'];

    function LoginController($location, Authentication) {
        var vm = this;
        vm.login = login;
        vm.resetPassword = resetPassword;

        activate();

        function activate() {
            // If the user is authenticated, they should not be here.
            if (Authentication.isAuthenticated()) {
                $location.url('/sightings');
            }
        }

        function login() {
            Authentication.login(vm.email, vm.password).then(successFn, errorFn);

            function successFn(response, status, headers, config) {
                Authentication.setAuthenticatedUser(response.data.data);
                $location.url('/sightings');
            }

            function errorFn(response, status, headers, config) {
                vm.error = response.status != 500 ? JSON.stringify(response.data) : response.statusText;
            }
        }

        function resetPassword() {
            window.location.href = '/user/password/reset/';
        }
    }
})();