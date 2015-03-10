(function () {
    'use strict';

    angular
        .module('ivigilate.authentication.controllers')
        .controller('LoginController', LoginController);

    LoginController.$inject = ['$location', '$scope', 'Authentication'];

    function LoginController($location, $scope, Authentication) {
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

            function successFn(data, status, headers, config) {
                Authentication.setAuthenticatedUser(data.data);
                $location.url('/sightings');
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
            }
        }

        function resetPassword() {
            window.location.href = '/user/password/reset/';
        }
    }
})();