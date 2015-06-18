(function () {
    'use strict';

    angular
        .module('ivigilate.sightings.controllers')
        .controller('EditSightingController', EditSightingController);

    EditSightingController.$inject = ['$location', '$scope', '$timeout', '$modalInstance', 'data', 'Authentication', 'Sightings'];

    function EditSightingController($location, $scope, $timeout, $modalInstance, data, Authentication, Sightings) {
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
            Sightings.update(vm.sighting).then(sightingSuccessFn, sightingErrorFn);

            function sightingSuccessFn(data, status, headers, config) {
                $modalInstance.close(vm.sighting);
            }

            function sightingErrorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
            }
        }

        function cancel() {
            $modalInstance.dismiss('Cancel');
        }
    }
})();