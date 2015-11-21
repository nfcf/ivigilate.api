(function () {
    'use strict';

    angular
        .module('ivigilate.sightings.controllers')
        .controller('AddSightingController', AddSightingController);
    
    AddSightingController.$inject = ['$location', '$scope', '$filter', '$modalInstance', 'data', 'Authentication',
                                    'Detectors', 'Beacons', 'Sightings'];

    function AddSightingController($location, $scope, $filter, $modalInstance, data, Authentication,
                                   Detectors, Beacons, Sightings) {
        var vm = this;
        vm.openDateTimePicker = openDateTimePicker;
        vm.cancel = cancel;
        vm.save = save;

        vm.error = undefined;
        vm.beacons = undefined;
        vm.beacon = undefined;
        vm.detectors = undefined;
        vm.detector = undefined;

        vm.seen_at_is_open = false;
        vm.duration_is_open = false;
        vm.max_date = $filter('date')(new Date(), 'yyyy-MM-dd');
        var now =  new Date();
        vm.seen_at = new Date(now.getFullYear(), now.getMonth(), now.getDate(), now.getHours(), (Math.ceil(now.getMinutes() / 5) * 5) - 15, 0);
        vm.duration = new Date(0, 0, 0, 0, 15);
        vm.comment = undefined;

        vm.date_options = {
            showWeeks: false,
            startingDay: 1
        };
        vm.time_options = {
            showMeridian: false,
            minuteStep: 5
        };

        activate();

        function activate() {
            var user = Authentication.getAuthenticatedUser();
            if (user) {
                populateDialog();
            }
            else {
                $location.url('/');
            }
        }

        function populateDialog(data) {
            Beacons.list().then(beaconsSuccessFn, beaconsErrorFn);

            function beaconsSuccessFn(data, status, headers, config) {
                vm.beacons = data.data;
            }

            function beaconsErrorFn(data, status, headers, config) {
                vm.error = 'Failed to get Beacons with error: ' + JSON.stringify(data.data);
            }

            Detectors.list().then(detectorsSuccessFn, detectorsErrorFn);

            function detectorsSuccessFn(data, status, headers, config) {
                vm.detectors = data.data;
            }

            function detectorsErrorFn(data, status, headers, config) {
                vm.error = 'Failed to get Detectors with error: ' + JSON.stringify(data.data);
            }
        }

        function openDateTimePicker($event, isOpen) {
            $event.preventDefault();
            $event.stopPropagation();
            vm[isOpen] = !vm[isOpen];
        }

        function save() {
            $scope.$broadcast('show-errors-check-validity');

            if (vm.form.$valid) {
                var sighting = {};
                sighting.beacon = vm.beacon.id;
                sighting.detector = vm.detector.id;
                sighting.first_seen_at = vm.seen_at;
                sighting.last_seen_at = addTime(vm.seen_at, vm.duration.getHours(), vm.duration.getMinutes());
                sighting.comment = vm.comment;
                sighting.confirmed = true;
                sighting.rssi = 0;

                Sightings.add(sighting).then(successFn, errorFn);
            } else {
                vm.error = 'There are invalid fields in the form.';
            }

            function successFn(data, status, headers, config) {
                $modalInstance.close(vm.sighting);
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
            }
        }

        function cancel() {
            $modalInstance.dismiss('Cancel');
        }

        function convertToUTC(dt) {
            return new Date(dt.getUTCFullYear(), dt.getUTCMonth(), dt.getUTCDate(), dt.getUTCHours(), dt.getUTCMinutes(), dt.getUTCSeconds());
        }

        function addTime(dt, hours, minutes) {
            return new Date(dt.getTime() + (hours * 3600000) + (minutes * 60000));
        }
    }
})();