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

                $interval(refresh, 10000);
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
                applyFilterToSightings();
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
            }
        }

        function addSighting(sighting) {
            var dlg = dialogs.create('static/templates/sightings/add_sighting.html', 'AddSightingController as vm', sighting, 'lg');
            dlg.result.then(function (addedSighting) {
                refresh();
            });
        }

        function editSighting(sighting) {
            var dlg = dialogs.create('static/templates/sightings/edit_sighting.html', 'EditSightingController as vm', sighting, 'lg');
            dlg.result.then(function (editedSighting) {
                refresh();
            });
        }

        function applyFilterToSightings() {
            if (vm.sightings) {
                var filterPlacesIds = undefined;
                if (vm.filterPlaces != null && vm.filterPlaces.length > 0) {
                    filterPlacesIds = [];
                    vm.filterPlaces.forEach(function (place) {
                        filterPlacesIds.push(place.id);
                    })
                }

                for (var i = 0; i < vm.sightings.length; i++) {
                    vm.sightings[i].satisfyFilter = vm.sightings[i].last_seen_at >= vm.filterDate &&
                                                    (filterPlacesIds === undefined || filterPlacesIds.indexOf(vm.sightings[i].place.id) >= 0);
                }
            }
        }

        function openDatePicker($event, isOpen) {
            $event.preventDefault();
            $event.stopPropagation();
            vm[isOpen] = !vm[isOpen];
        }

    }
})();