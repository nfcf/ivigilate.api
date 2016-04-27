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
        vm.editDetector= editDetector;
        vm.confirmSighting = confirmSighting;
        vm.openDatePicker = openDatePicker;

        vm.sightings = undefined;
        vm.filterDate = vm.filterDateMax = $filter('date')(new Date(), 'yyyy-MM-dd');
        vm.filterDateIsOpen = false;

        vm.fixedBeaconsAndDetectors = [];
        vm.filterFixedBeaconsAndDetectors = [];

        vm.filterShowAll = false;

        vm.datepickerOptions = {
            showWeeks: false,
            startingDay: 1
        };

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

            $scope.$watch('vm.filterDate', function () {
                vm.filterDate = $filter('date')(vm.filterDate, 'yyyy-MM-dd');
                refresh();
            });

            $scope.$watch('vm.filterFixedBeaconsAndDetectors', function () {
                refresh();
            });

            $scope.$watch('vm.filterShowAll', function () {
                refresh();
            });

            var refreshInterval = $interval(refresh, 2000);
            $scope.$on('$destroy', function () {
                $interval.cancel(refreshInterval);
            });

            function beaconsSuccessFn(data, status, headers, config) {
                var fixedBeacons = data.data;
                for (var i = 0; i < fixedBeacons.length; i++) {
                    if (fixedBeacons[i].type == 'M') fixedBeacons.splice(i--, 1);
                    else fixedBeacons[i].kind = fixedBeacons[i].type_display + ' Beacon';
                }
                vm.fixedBeaconsAndDetectors.extend(fixedBeacons);
            }

            function detectorsSuccessFn(data, status, headers, config) {
                var fixedDetectors = data.data;
                for (var i = 0; i < fixedDetectors.length; i++) {
                    if (fixedDetectors[i].type == 'M') fixedDetectors.splice(i--, 1);
                    else fixedDetectors[i].kind = fixedDetectors[i].type_display + ' Detector';
                }
                vm.fixedBeaconsAndDetectors.extend(fixedDetectors);
            }

            function errorFn(data, status, headers, config) {
                vm.error = 'Failed to get filter data with error: ' +
                data.status != 500 ? JSON.stringify(data.data) : data.statusText;
            }
        }

        function refresh() {
            if (vm.filterDate) {
                Sightings.list(vm.filterDate, vm.filterFixedBeaconsAndDetectors, vm.filterShowAll).then(successFn, errorFn);
                Notifications.checkForNotifications();
            }

            function successFn(response, status, headers, config) {
                vm.error = null;
                vm.sightings = sortByKey(response.data.data, 'id');

                applyClientServerTimeOffset(response.data.timestamp);

                applyFilterAndPreventTimesInTheFutureToSightings();
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
                vm.sightings[i].last_seen_at = new Date(vm.sightings[i].last_seen_at).getTime() - offset;
                vm.sightings[i].last_seen_at = new Date(vm.sightings[i].last_seen_at).toISOString();
            }
        }

        function applyFilterAndPreventTimesInTheFutureToSightings() {
            if (vm.sightings) {
                var filterFixedBeaconsAndDetectorsIds = undefined;
                if (vm.filterFixedBeaconsAndDetectors != null && vm.filterFixedBeaconsAndDetectors.length > 0) {
                    filterFixedBeaconsAndDetectorsIds = [];
                    vm.filterFixedBeaconsAndDetectors.forEach(function (fixedBeaconOrDetector) {
                        filterFixedBeaconsAndDetectorsIds.push(fixedBeaconOrDetector.kind.replace(' ', '') + fixedBeaconOrDetector.id);
                    })
                }

                var now = new Date();
                for (var i = 0; i < vm.sightings.length; i++) {
                    if (new Date(vm.sightings[i].last_seen_at) > now) {
                        vm.sightings[i].last_seen_at = now;
                    }

                    vm.sightings[i].satisfyFilter = new Date(vm.sightings[i].last_seen_at) >= new Date(vm.filterDate + ' 00:00:00') &&
                    (filterFixedBeaconsAndDetectorsIds === undefined ||
                    (!!vm.sightings[i].beacon && filterFixedBeaconsAndDetectorsIds.indexOf('FixedBeacon' + vm.sightings[i].beacon.id) >= 0) ||
                    (!!vm.sightings[i].detector &&
                        (filterFixedBeaconsAndDetectorsIds.indexOf('FixedDetector' + vm.sightings[i].detector.id) >= 0 ||
                         filterFixedBeaconsAndDetectorsIds.indexOf('UserDetector' + vm.sightings[i].detector.id) >= 0)));
                }
            }
        }

        function openDatePicker($event, isOpen) {
            $event.preventDefault();
            $event.stopPropagation();
            vm[isOpen] = !vm[isOpen];
        }

        function sortByKey(array, key) {
            return array.sort(function(a, b) {
                var x = a[key];
                var y = b[key];

                if (typeof x == "string")
                {
                    x = x.toLowerCase();
                    y = y.toLowerCase();
                }

                return ((x < y) ? -1 : ((x > y) ? 1 : 0));
            });
        }

        Array.prototype.extend = function (other_array) {
            /* should include a test to check whether other_array really is an array... */
            other_array.forEach(function (v) {
                this.push(v)
            }, this);
        }
    }
})();