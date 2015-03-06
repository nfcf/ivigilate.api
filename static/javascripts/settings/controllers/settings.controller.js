(function () {
    'use strict';

    angular
        .module('ivigilate.settings.controllers')
        .controller('SettingsController', SettingsController);

    SettingsController.$inject = ['$location', '$scope', 'Authentication', 'Settings'/*, 'Snackbar'*/];

    function SettingsController($location, $scope, Authentication, Settings/*, Snackbar*/) {
        var vm = this;
        vm.update = update;

        vm.success = undefined;
        vm.error = undefined;
        vm.user = undefined;

        activate();

        function activate() {
            var user = Authentication.getAuthenticatedUser();
            if (user) {
                Settings.get(user.id).then(successFn, errorFn);
            }
            else {
                $location.url('/');
            }

            function successFn(data, status, headers, config) {
                vm.user = data.data;
            }

            function errorFn(data, status, headers, config) {
                $location.url('/');
                Snackbar.error('That user does not exist.');
            }
        }

        function update() {
            if (vm.user.password !== undefined && vm.user.password.trim() === "") vm.user.password = undefined;
            Settings.update(vm.user).then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                vm.error = null;
                vm.success = 'Your profile has been updated.';
            }

            function errorFn(data, status, headers, config) {
                vm.success = null;
                vm.error = 'Failed to update settings with error: ' + JSON.stringify(data.data);
            }
        }
    }
})();