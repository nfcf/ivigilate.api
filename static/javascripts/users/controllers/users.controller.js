(function () {
    'use strict';

    angular
        .module('ivigilate.users.controllers')
        .controller('UsersController', UsersController);

    UsersController.$inject = ['$location', '$scope', '$timeout', 'Authentication', 'Users'];

    function UsersController($location, $scope, $timeout, Authentication, Users) {
        var vm = this;
        vm.update = update;
        vm.updateUserActiveState = updateUserActiveState;
        vm.updateUserAdminState = updateUserAdminState;

        vm.success = undefined;
        vm.error = undefined;

        vm.user = undefined;
        vm.users = undefined;
        vm.original_email = undefined;

        activate();

        function activate() {
            var user = Authentication.getAuthenticatedUser();
            if (user) {
                Users.get(user.id).then(getUserSuccessFn, errorFn);
            }
            else {
                $location.url('/');
            }

            function getUserSuccessFn(data, status, headers, config) {
                vm.user = data.data;
                vm.original_email = vm.user.email;

                if (vm.user.is_account_admin) {
                    Users.list().then(listUsersSuccessFn, errorFn);
                }
            }

            function listUsersSuccessFn(data, status, headers, config) {
                vm.users = data.data;
            }

            function errorFn(data, status, headers, config) {
                $location.url('/');
            }
        }

        function update() {
            if (vm.user.password !== undefined && vm.user.password.trim() === '') vm.user.password = undefined;
            if (vm.user.confirm_password !== undefined && vm.user.confirm_password.trim() === '') vm.user.confirm_password = undefined;

            $scope.$broadcast('show-errors-check-validity');

            if (vm.form.$valid) {
                Users.update(vm.user).then(successFn, errorFn);
            } else {
                if (vm.user.email != vm.original_email &&
                    (vm.user.password == undefined || vm.user.confirm_password == undefined)) {
                    vm.error = 'You need to provide your password to be able to change your email address.';
                } else {
                    vm.error = 'There are invalid fields in the form.';
                }
                vm.success = null;
            }

            function successFn(data, status, headers, config) {
                Authentication.setAuthenticatedUser(data.data);
                vm.error = null;
                vm.success = 'Your settings have been updated.';
            }

            function errorFn(data, status, headers, config) {
                vm.success = null;
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
            }
        }

        function updateUserAdminState(user) {
            Users.update(user).then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                // Do nothing...
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
                user.is_account_admin = !user.is_account_admin;
            }
        }

        function updateUserActiveState(user) {
            Users.update(user).then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                // Do nothing...
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
                user.is_active = !user.is_active;
            }
        }

    }
})();