(function () {
    'use strict';

    angular
        .module('ivigilate.sightings.controllers')
        .controller('SightingsController', SightingsController);

    SightingsController.$inject = ['$location', '$scope', '$filter', '$interval', 'Authentication', 'Places', 'Sightings', 'dialogs'];

    function SightingsController($location, $scope, $filter, $interval, Authentication, Places, Sightings, dialogs) {
        var vm = this;
        vm.refresh = refresh;
        vm.addSighting = addSighting;
        vm.editSighting = editSighting;
        vm.confirmSighting = confirmSighting;
        vm.openDatePicker = openDatePicker;

        vm.sightings = undefined;
        vm.filterDate = vm.filterDateMax = $filter('date')(new Date(), 'yyyy-MM-dd');
        vm.filterDateIsOpen = false;

        vm.places = undefined;
        vm.filterPlaces = [];

        vm.filterShowAll = false;

        vm.datepickerOptions = {
            showWeeks: false,
            startingDay: 1
        };

        activate();

        function activate() {
            var user = Authentication.getAuthenticatedUser();
            if (user) {
                Places.list().then(placesSuccessFn, placesErrorFn);

                $scope.$watch('vm.filterDate', function () {
                    vm.filterDate = $filter('date')(vm.filterDate, 'yyyy-MM-dd');
                    refresh();
                });

                $scope.$watch('vm.filterPlaces', function () {
                    refresh();
                });

                $scope.$watch('vm.filterShowAll', function () {
                    refresh();
                });

                var refreshInterval = $interval(refresh, 15000);
                $scope.$on('$destroy', function () { $interval.cancel(refreshInterval); });
            }
            else {
                $location.url('/');
            }

            function placesSuccessFn(data, status, headers, config) {
                vm.places = data.data;
            }

            function placesErrorFn(data, status, headers, config) {
                vm.error = 'Failed to get Places with error: ' + JSON.stringify(data.data);
            }
        }

        function refresh() {
            if (vm.filterDate) {
                Sightings.list(vm.filterDate, vm.filterPlaces, vm.filterShowAll).then(successFn, errorFn);
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
            var dlg = dialogs.create('static/templates/sightings/addsighting.html', 'AddSightingController as vm', null, 'lg');
            dlg.result.then(function (newSighting) {
                refresh();
            });
        }

        function editSighting(sighting) {
            var dlg = dialogs.create('static/templates/sightings/editsighting.html', 'EditSightingController as vm', sighting, 'lg');
            dlg.result.then(function (editedSighting) {
                refresh();
            });
        }

        function confirmSighting(sighting) {
            var sightingToSend = JSON.parse(JSON.stringify(sighting));
            sightingToSend.movable = sightingToSend.movable.id;  // Required for the REST serializer
            sightingToSend.place = sightingToSend.place.id;  // Required for the REST serializer
            Sightings.update(sightingToSend).then(successFn, errorFn);

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
                var filterPlacesIds = undefined;
                if (vm.filterPlaces != null && vm.filterPlaces.length > 0) {
                    filterPlacesIds = [];
                    vm.filterPlaces.forEach(function (place) {
                        filterPlacesIds.push(place.id);
                    })
                }

                var now = new Date();
                for (var i = 0; i < vm.sightings.length; i++) {
                    if (new Date(vm.sightings[i].last_seen_at) > now) {
                        vm.sightings[i].last_seen_at = now;
                    }
                    //vm.sightings[i].first_seen_at = convertUTCDateToLocalDate(new Date(vm.sightings[i].first_seen_at));
                    //vm.sightings[i].last_seen_at = convertUTCDateToLocalDate(new Date(vm.sightings[i].last_seen_at));
                    vm.sightings[i].satisfyFilter = new Date(vm.sightings[i].last_seen_at) >= new Date(vm.filterDate) &&
                    (filterPlacesIds === undefined || filterPlacesIds.indexOf(vm.sightings[i].place.id) >= 0);
                }
            }
        }

        function openDatePicker($event, isOpen) {
            $event.preventDefault();
            $event.stopPropagation();
            vm[isOpen] = !vm[isOpen];
        }

        function convertUTCDateToLocalDate(date) {
            var newDate = new Date(date.getTime() + date.getTimezoneOffset() * 60 * 1000);

            var offset = date.getTimezoneOffset() / 60;
            var hours = date.getHours();

            newDate.setHours(hours - offset);

            return newDate;
        }
    }
})();