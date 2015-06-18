(function () {
    'use strict';

    angular
        .module('ivigilate.authentication.controllers')
        .controller('RegisterController', RegisterController);

    RegisterController.$inject = ['$location', 'Authentication'];

    function RegisterController($location, Authentication) {
        var vm = this;
        vm.register = register;

        activate();

        function activate() {
            // If the user is authenticated, they should not be here.
            if (Authentication.isAuthenticated()) {
                $location.url('/');
            }
        }

        function register() {
            Authentication.register(vm.company_id, vm.email, vm.password).then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                Authentication.login(vm.email, vm.password).then(successFn, errorFn);

                function successFn(data, status, headers, config) {
                    Authentication.setAuthenticatedUser(data.data);
                    window.location = '/'; //use this instead of $location.url to force refresh the navbar
                }

                function errorFn(data, status, headers, config) {
                    vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
                }
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
            }
        }
    }
})();