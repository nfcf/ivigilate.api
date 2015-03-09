(function () {
    'use strict';

    angular
        .module('ivigilate.layout.controllers')
        .controller('NavbarController', NavbarController);

    NavbarController.$inject = ['$location', '$scope', '$rootScope', 'Authentication'];

    function NavbarController($location, $scope, $rootScope, Authentication) {
        var vm = this;

        vm.init = init;
        vm.logout = logout;

        vm.userEmail = undefined;
        vm.user = undefined;

        $rootScope.$on('IS_AUTHENTICATED', function (event, data) {
            if (data) {
                vm.user = Authentication.getAuthenticatedUser();
                if (vm.user) {
                    vm.user.username = vm.user.email.split('@')[0];
                }
            } else {
                vm.user = undefined;
            }
        });

        function init(emailFromServer) {
            var user = Authentication.getAuthenticatedUser();
            if (emailFromServer && user && emailFromServer === user.email) {
                Authentication.isAuthenticated();
            } else {
                Authentication.unauthenticate();
            }
        }

        function logout() {
            Authentication.logout().then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                Authentication.unauthenticate();
                $location.url('/login');
            }

            function errorFn(data, status, headers, config) {
                console.error('Logout failure!');
            }
        }
    }
})();