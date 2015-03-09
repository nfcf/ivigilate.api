(function () {
    'use strict';

    angular
        .module('ivigilate.places.controllers')
        .controller('AddSightingController', AddSightingController);

    AddSightingController.$inject = ['$location', '$scope', '$modalInstance', 'data', 'Authentication', 'Places', 'Movables'];

    function AddSightingController($location, $scope, $modalInstance, data, Authentication, Places, Movables) {
        var vm = this;
        vm.cancel = cancel;
        vm.save = save;

        vm.error = undefined;
        vm.sighting = undefined;
        vm.movables = undefined;
        vm.places = undefined;
        vm.durations = [1,5,10,15,20,30,45,60,90,120,150,180,210,240];

        activate();

        function activate() {
            var user = Authentication.getAuthenticatedUser();
            if (user) {
                populateDialog(data, user);
            }
            else {
                $location.url('/');
            }
        }

        function populateDialog(data, user) {
            vm.sighting = data;

            Movables.list().then(movablesSuccessFn, movablesErrorFn);

            function movablesSuccessFn(data, status, headers, config) {
                vm.movables = data.data;
            }

            function movablesErrorFn(data, status, headers, config) {
                vm.error = 'Failed to get Movables with error: ' + JSON.stringify(data.data.message);
            }

            Places.list().then(placesSuccessFn, placesErrorFn);

            function placesSuccessFn(data, status, headers, config) {
                vm.places = data.data;
            }

            function placesErrorFn(data, status, headers, config) {
                vm.error = 'Failed to get Places with error: ' + JSON.stringify(data.data.message);
            }
        }

        function save() {
            Sightings.add(vm.sighting).then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                $modalInstance.close(vm.sighting);
            }

            function errorFn(data, status, headers, config) {
                vm.error = 'Failed to add Sighting with error: ' + JSON.stringify(data.data.message);
            }
        }

        function cancel() {
            $modalInstance.dismiss('Cancel');
        }
    }
})();