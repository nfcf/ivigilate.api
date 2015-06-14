(function () {
    'use strict';

    angular
        .module('ivigilate.places.controllers')
        .controller('AddSightingController', AddSightingController);
    
    AddSightingController.$inject = ['$location', '$scope', '$filter', '$modalInstance', 'data', 'Authentication',
                                    'Places', 'Beacons', 'Sightings'];

    function AddSightingController($location, $scope, $filter, $modalInstance, data, Authentication,
                                   Places, Beacons, Sightings) {
        var vm = this;
        vm.openDatePicker = openDatePicker;
        vm.cancel = cancel;
        vm.save = save;

        vm.error = undefined;
        vm.beacons = undefined;
        vm.beacon = undefined;
        vm.places = undefined;
        vm.place = undefined;

        vm.datepickerOpen = false;
        vm.seen_at_date = vm.maxDate = $filter('date')(new Date(), 'yyyy-MM-dd');
        vm.seen_at = new Date();
        vm.duration = new Date(0, 0, 0, 0, 15);
        vm.comment = undefined;

        vm.datepickerOptions = {
            showWeeks: false,
            startingDay: 1
        };

        activate();

        function activate() {
            var user = Authentication.getAuthenticatedUser();
            if (user) {
                populateDialog();

                $scope.$watch('vm.seen_at_date', function () {
                    var dateParts = (vm.seen_at_date instanceof Date) ? vm.seen_at_date.toISOString().split('-') : vm.seen_at_date.split('-');
                    vm.seen_at = new Date(dateParts[0], dateParts[1] - 1, dateParts[2].slice(0, 2), vm.seen_at.getHours(), vm.seen_at.getMinutes());
                });
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

            Places.list().then(placesSuccessFn, placesErrorFn);

            function placesSuccessFn(data, status, headers, config) {
                vm.places = data.data;
            }

            function placesErrorFn(data, status, headers, config) {
                vm.error = 'Failed to get Places with error: ' + JSON.stringify(data.data);
            }
        }

        function openDatePicker($event, isOpen) {
            $event.preventDefault();
            $event.stopPropagation();
            vm[isOpen] = !vm[isOpen];
        }

        function save() {
            var sighting = {};
            sighting.beacon = vm.beacon.id;
            sighting.place = vm.place.id;
            sighting.first_seen_at = vm.seen_at;
            sighting.last_seen_at = addTime(vm.seen_at, vm.duration.getHours(), vm.duration.getMinutes());
            sighting.comment = vm.comment;
            sighting.confirmed = true;

            Sightings.add(sighting).then(successFn, errorFn);

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