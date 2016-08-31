(function () {
    'use strict';

    angular
        .module('ivigilate.sightings.controllers')
        .controller('EditSightingController', EditSightingController);

    EditSightingController.$inject = ['$location', '$scope', '$timeout', '$uibModalInstance', 'data', 'Authentication', 'Sightings'];

    function EditSightingController($location, $scope, $timeout, $uibModalInstance, data, Authentication, Sightings) {
        var vm = this;
        vm.cancel = cancel;
        vm.save = save;

        vm.error = undefined;
        vm.sighting = undefined;

        activate();

        function activate() {
            var user = Authentication.getAuthenticatedUser();
            if (user) {
                vm.sighting = data;
            }
            else {
                $location.url('/');
            }
        }

        function save() {
            $scope.$broadcast('show-errors-check-validity');

            if (vm.form.$valid) {
                Sightings.update(vm.sighting).then(successFn, errorFn);
            } else {
                vm.error = 'There are invalid fields in the form.';
            }

            function successFn(data, status, headers, config) {
                $uibModalInstance.close(vm.sighting);
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
            }
        }

        function cancel() {
            $uibModalInstance.dismiss('Cancel');
        }
    }
})();