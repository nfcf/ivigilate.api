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

        function init(isAuthenticated) {
            if (!isAuthenticated) {
                Authentication.unauthenticate();
            } else {
                Authentication.isAuthenticated();
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