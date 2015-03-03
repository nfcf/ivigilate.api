(function () {
    'use strict';

    angular
        .module('ivigilate.authentication.controllers')
        .controller('RegisterController', RegisterController);

    RegisterController.$inject = ['$location', '$scope', 'Authentication'];

    function RegisterController($location, $scope, Authentication) {
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
            Authentication.register(vm.company_id, vm.email, vm.password);
        }
    }
})();