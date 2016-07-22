(function () {
    'use strict';

    angular
        .module('ivigilate.sightings.controllers')
        .controller('SightingsController', SightingsController);

    SightingsController.$inject = ['$location', '$scope', '$filter', '$interval', 'Authentication',
        'Users', 'Beacons', 'Detectors', 'Sightings', 'Payments', 'dialogs', 'Notifications'];

    function SightingsController($location, $scope, $filter, $interval, Authentication,
                                 Users, Beacons, Detectors, Sightings, Payments, dialogs, Notifications) {
        var vm = this;
        vm.refresh = refresh;
        vm.addSighting = addSighting;
        vm.editSighting = editSighting;
        vm.editBeacon = editBeacon;
        vm.editDetector = editDetector;
        vm.confirmSighting = confirmSighting;
        vm.openDatePicker = openDatePicker;
        vm.viewGps = viewGps;

        vm.sightings = undefined;
        vm.formattedSightings = undefined;

        vm.filterStartDate = vm.filterDateMax = $filter('date')(new Date(), 'yyyy-MM-dd');
        vm.filterDateIsOpen = false;

        vm.filterEndDate = vm.filterDateMax = $filter('date')(new Date(), 'yyyy-MM-dd');
        vm.filterEndDateIsOpen = false;

        vm.beaconsOrDetectors = [];
        vm.filterBeaconOrDetector = undefined;

        vm.sightingType = [{'type': 'Beacon', 'description': 'Show only Beacon Sightings'},
            {'type': 'GPS', 'description': 'Show only GPS Sightings'}];
        vm.filterSightingType = undefined;
        vm.filteredSightings = undefined;


        vm.datepickerOptions = {
            showWeeks: false,
            startingDay: 1
        };

        vm.resetValue = function ($event) {
            vm.filterBeaconOrDetector = null;
            $event.stopPropagation();
        };

        vm.resetType = function ($event) {
            vm.filterSightingType = null;
            $event.stopPropagation();
        }

        activate();


        function activate() {
            var user = Authentication.getAuthenticatedUser();
            if (user) {
                Payments.checkLicense(user).then(function () {
                    initAndRefresh();
                });
            }
            else {
                $location.url('/');
            }
        }

        function initAndRefresh() {
            Beacons.list().then(beaconsSuccessFn, errorFn);
            Detectors.list().then(detectorsSuccessFn, errorFn);

            $scope.$watch('vm.filterStartDate', function () {
                vm.filterStartDate = $filter('date')(vm.filterStartDate, 'yyyy-MM-dd');
                refresh();
            });

            $scope.$watch('vm.filterEndDate', function () {
                vm.filterEndDate = $filter('date')(vm.filterEndDate, 'yyyy-MM-dd');
                refresh();
            });


            $scope.$watch('vm.filterBeaconOrDetector', function () {
                refresh();
            });

            var refreshInterval = $interval(refresh, 2000);
            $scope.$on('$destroy', function () {
                $interval.cancel(refreshInterval);
            });

            function beaconsSuccessFn(data, status, headers, config) {
                var beacons = data.data;
                for (var i = 0; i < beacons.length; i++) {
                    beacons[i].kind = beacons[i].type_display + ' Beacon';
                }
                vm.beaconsOrDetectors.extend(beacons);
            }

            function detectorsSuccessFn(data, status, headers, config) {
                var detectors = data.data;
                for (var i = 0; i < detectors.length; i++) {
                    detectors[i].kind = detectors[i].type_display + ' Detector';
                }
                vm.beaconsOrDetectors.extend(detectors);
            }

            function errorFn(data, status, headers, config) {
                vm.error = 'Failed to get filter data with error: ' +
                data.status != 500 ? JSON.stringify(data.data) : data.statusText;
            }
        }

        function refresh() {
            if (vm.filterStartDate) {
                Sightings.list(vm.filterStartDate, vm.filterEndDate, vm.filterBeaconOrDetector, vm.filterShowAll).then(successFn, errorFn);
                Notifications.checkForNotifications();

            }

            function successFn(response, status, headers, config) {
                vm.error = null;
                vm.sightings = sortByKey(response.data.data, 'id');
                applyClientServerTimeOffset(response.data.timestamp);

                filterSightingsByType();

                setTimeout(prepareSightingsForExport, 50);
            }

            function errorFn(response, status, headers, config) {
                vm.error = response.status != 500 ? JSON.stringify(response.data) : response.statusText;
            }
        }

        function addSighting() {
            var dlg = dialogs.create('static/templates/sightings/addsighting.html', 'AddSightingController as vm', null, {'size': 'md'});
            dlg.result.then(function (newSighting) {
                refresh();
            });
        }

        function editSighting(sighting) {
            var dlg = dialogs.create('static/templates/sightings/editsighting.html', 'EditSightingController as vm', sighting, {'size': 'md'});
            dlg.result.then(function (editedSighting) {
                refresh();
            });
        }

        function editBeacon(beacon) {
            var dlg = dialogs.create('static/templates/beacons/editbeacon.html', 'EditBeaconController as vm', beacon, {'size': 'lg'});
            dlg.result.then(function (editedBeacon) {
                refresh();
            });
        }

        function editDetector(detector) {
            var dlg = dialogs.create('static/templates/detectors/editdetector.html', 'EditDetectorController as vm', detector, {'size': 'lg'});
            dlg.result.then(function (editedDetector) {
                refresh();
            });
        }

        function viewGps(sighting) {
            var dlg = dialogs.create('static/templates/sightings/viewgps.html', 'ViewGpsController as vm', sighting, {'size': 'lg'});
        }

        function confirmSighting(sighting) {
            Sightings.update(sighting).then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                // Do nothing...
            }

            function errorFn(response, status, headers, config) {
                vm.error = response.status != 500 ? JSON.stringify(response.data) : response.statusText;
                sighting.confirmed = !sighting.confirmed;
            }
        }

        function applyClientServerTimeOffset(serverTimestamp) {
            var offset = new Date(serverTimestamp).getTime() - (new Date()).getTime();
            for (var i = 0; i < vm.sightings.length; i++) {
                vm.sightings[i].first_seen_at = new Date(vm.sightings[i].first_seen_at).getTime() - offset;
                vm.sightings[i].first_seen_at = new Date(vm.sightings[i].first_seen_at).toISOString();
                vm.sightings[i].last_seen_at = new Date(vm.sightings[i].last_seen_at).getTime() - offset;
                vm.sightings[i].last_seen_at = new Date(vm.sightings[i].last_seen_at).toISOString();
            }
        }

        function preventTimesInTheFutureToSightings() {
            if (vm.sightings) {
                var now = new Date();
                for (var i = 0; i < vm.sightings.length; i++) {
                    if (new Date(vm.sightings[i].last_seen_at) > now) {
                        vm.sightings[i].last_seen_at = now;
                    }
                }
            }
        }

        function openDatePicker($event, isOpen) {
            $event.preventDefault();
            $event.stopPropagation();
            vm[isOpen] = !vm[isOpen];
        }

        function sortByKey(array, key) {
            return array.sort(function (a, b) {
                var x = a[key];
                var y = b[key];

                if (typeof x == "string") {
                    x = x.toLowerCase();
                    y = y.toLowerCase();
                }

                return ((x < y) ? -1 : ((x > y) ? 1 : 0));
            });
        }

        function filterSightingsByType() {
            if (!vm.filterSightingType) {
                return;
            }
            vm.filteredSightings = [];
            for (var i = 0 ; i < vm.sightings.length ; i++) {
                if (vm.filterSightingType.type === 'GPS' && vm.sightings[i].type === vm.filterSightingType.type ||
                    vm.filterSightingType.type === 'Beacon' && vm.sightings[i].type !== 'GPS') {
                    vm.filteredSightings.push(vm.sightings[i]);
                }
            }
            vm.sightings = vm.filteredSightings;
        }

        //formats sightings for exportation to CSV format
        function prepareSightingsForExport() {
            //todo: needs some improvement
            vm.formattedSightings = [];
            if (!vm.sightings || !vm.sightings.length > 0) {
                return;
            }
            var formattedSighting;
            var fields = ['beacon', 'beacon_id', 'detector', 'detector_id', 'first_seen_at', 'last_seen_at', 'location',
                'beacon_battery', 'confirmed', 'detector_battery'];

            for (var i = 0; i < vm.sightings.length; i++) {
                formattedSighting = {};
                for (var prop in vm.sightings[i]) {

                    if (fields.includes(prop)) {
                        if (prop === 'beacon' || prop === 'detector') {
                            formattedSighting[prop + '_name'] = vm.sightings[i][prop] != null ? vm.sightings[i][prop]['name'] : 'GPS';
                            formattedSighting[prop + '_id'] = vm.sightings[i][prop] != null ? vm.sightings[i][prop]['id'] : 'N/A'
                            continue;
                        } else if (prop == 'location' && vm.sightings[i][prop] != null) {
                            formattedSighting['location'] = vm.sightings[i][prop]['coordinates'][0] + ', ' +
                                vm.sightings[i][prop]['coordinates'][1];
                            continue;
                        }
                        formattedSighting[prop] = vm.sightings[i][prop];
                    }
                }
                vm.formattedSightings.push(formattedSighting);
            }
        }

        Array.prototype.extend = function (other_array) {
            /* should include a test to check whether other_array really is an array... */
            other_array.forEach(function (v) {
                this.push(v)
            }, this);
        }
    }
})();