(function () {
    'use strict';

    angular
        .module('ivigilate.sightings.controllers')
        .controller('SightingsController', SightingsController);

    SightingsController.$inject = ['$location', '$scope', '$filter', '$interval', 'Authentication',
        'Users', 'Beacons', 'Detectors', 'Sightings', 'Payments', 'dialogs'];

    function SightingsController($location, $scope, $filter, $interval, Authentication,
                                 Users, Beacons, Detectors, Sightings, Payments, dialogs) {
        var vm = this;
        vm.refresh = refresh;
        vm.addSighting = addSighting;
        vm.editSighting = editSighting;
        vm.confirmSighting = confirmSighting;
        vm.openDatePicker = openDatePicker;

        vm.sightings = undefined;
        vm.filterDate = vm.filterDateMax = $filter('date')(new Date(), 'yyyy-MM-dd');
        vm.filterDateIsOpen = false;

        vm.placesAndUsers = [];
        vm.filterPlacesAndUsers = [];

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
            Users.list().then(usersSuccessFn, errorFn);

            $scope.$watch('vm.filterDate', function () {
                vm.filterDate = $filter('date')(vm.filterDate, 'yyyy-MM-dd');
                refresh();
            });

            $scope.$watch('vm.filterPlacesAndUsers', function () {
                refresh();
            });

            $scope.$watch('vm.filterShowAll', function () {
                refresh();
            });

            var refreshInterval = $interval(refresh, 15000);
            $scope.$on('$destroy', function () {
                $interval.cancel(refreshInterval);
            });

            function beaconsSuccessFn(data, status, headers, config) {
                var fixedBeacons = data.data;
                for (var i = 0; i < fixedBeacons.length; i++) {
                    if (fixedBeacons[i].type != 'F') fixedBeacons.splice(i--, 1);
                    else fixedBeacons[i].kind = 'Fixed Beacon';
                }
                vm.placesAndUsers.extend(fixedBeacons);
            }

            function detectorsSuccessFn(data, status, headers, config) {
                var fixedDetectors = data.data;
                for (var i = 0; i < fixedDetectors.length; i++) {
                    if (fixedDetectors[i].type != 'F') fixedDetectors.splice(i--, 1);
                    else fixedDetectors[i].kind = 'Fixed Detector';
                }
                vm.placesAndUsers.extend(fixedDetectors);
            }

            function usersSuccessFn(data, status, headers, config) {
                var users = data.data;
                users.forEach(function (placeOrUser) {
                        placeOrUser.kind = 'User';
                    });
                vm.placesAndUsers.extend(users);
            }

            function errorFn(data, status, headers, config) {
                vm.error = 'Failed to get filter data with error: ' +
                data.status != 500 ? JSON.stringify(data.data) : data.statusText;
            }
        }

        function refresh() {
            if (vm.filterDate) {
                Sightings.list(vm.filterDate, vm.filterPlacesAndUsers, vm.filterShowAll).then(successFn, errorFn);
            }

            function successFn(data, status, headers, config) {
                vm.error = null;
                vm.sightings = data.data;
                applyFilterAndPreventTimesInTheFutureToSightings();
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
            }
        }

        function addSighting() {
            var dlg = dialogs.create('static/templates/sightings/addsighting.html', 'AddSightingController as vm', null, {'size': 'lg'});
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

        function confirmSighting(sighting) {
            Sightings.update(sighting).then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                // Do nothing...
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
                sighting.confirmed = !sighting.confirmed;
            }
        }

        function applyFilterAndPreventTimesInTheFutureToSightings() {
            if (vm.sightings) {
                var filterPlacesAndUsersIds = undefined;
                if (vm.filterPlacesAndUsers != null && vm.filterPlacesAndUsers.length > 0) {
                    filterPlacesAndUsersIds = [];
                    vm.filterPlacesAndUsers.forEach(function (placeOrUser) {
                        filterPlacesAndUsersIds.push(placeOrUser.kind.replace(' ', '') + placeOrUser.id);
                    })
                }

                var now = new Date();
                for (var i = 0; i < vm.sightings.length; i++) {
                    if (new Date(vm.sightings[i].last_seen_at) > now) {
                        vm.sightings[i].last_seen_at = now;
                    }
                    vm.sightings[i].satisfyFilter = new Date(vm.sightings[i].last_seen_at) >= new Date(vm.filterDate) &&
                    (filterPlacesAndUsersIds === undefined ||
                    (!!vm.sightings[i].beacon && filterPlacesAndUsersIds.indexOf('FixedBeacon' + vm.sightings[i].beacon.id) >= 0) ||
                    (!!vm.sightings[i].detector && filterPlacesAndUsersIds.indexOf('FixedDetector' + vm.sightings[i].detector.id) >= 0) ||
                    (!!vm.sightings[i].user && vm.sightings[i].beacon.type == 'M' && filterPlacesAndUsersIds.indexOf('User' + vm.sightings[i].user.id) >= 0));
                }
            }
        }

        function openDatePicker($event, isOpen) {
            $event.preventDefault();
            $event.stopPropagation();
            vm[isOpen] = !vm[isOpen];
        }

        Array.prototype.extend = function (other_array) {
            /* should include a test to check whether other_array really is an array... */
            other_array.forEach(function (v) {
                this.push(v)
            }, this);
        }
    }
})();