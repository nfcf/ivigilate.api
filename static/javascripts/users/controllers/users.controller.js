(function () {
    'use strict';

    angular
        .module('ivigilate.users.controllers')
        .controller('UsersController', UsersController);

    UsersController.$inject = ['$location', '$scope', '$timeout', 'Authentication', 'Users'];

    function UsersController($location, $scope, $timeout, Authentication, Users) {
        var vm = this;
        vm.fileChanged = fileChanged;
        vm.update = update;
        vm.updateUserActiveState = updateUserActiveState;
        vm.updateUserAdminState = updateUserAdminState;

        vm.success = undefined;
        vm.error = undefined;

        vm.user = undefined;
        vm.users = undefined;
        vm.imagePreview = undefined;
        vm.imageToUpload = undefined;

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
                vm.imagePreview = vm.user.photo;

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

        function fileChanged(files) {
            if (files && files[0]) {
                var fileReader = new FileReader();
                fileReader.onload = function (e) {
                    $scope.$apply(function () {
                        vm.imageToUpload = files[0];
                        $timeout(function () {
                            vm.imagePreview = fileReader.result;
                        }, 250);
                    });
                };
                fileReader.readAsDataURL(files[0]);
            } else {
                vm.imagePreview = null;
            }
        }

        function update() {
            $scope.$broadcast('show-errors-check-validity');

            if (vm.form.$valid) {
                if (vm.user.password !== undefined && vm.user.password.trim() === '') vm.user.password = undefined;
                Users.update(vm.user, vm.imageToUpload).then(successFn, errorFn);
            } else {
                vm.error = 'There are invalid fields in the form.';
            }

            function successFn(data, status, headers, config) {
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