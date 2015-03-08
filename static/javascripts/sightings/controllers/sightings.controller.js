(function () {
    'use strict';

    angular
        .module('ivigilate.sightings.controllers')
        .controller('SightingsController', SightingsController);

    SightingsController.$inject = ['$location', '$scope', '$filter', '$interval', 'Authentication', 'Sightings', 'dialogs'];

    function SightingsController($location, $scope, $filter, $interval, Authentication, Sightings, dialogs) {
        var vm = this;
        vm.refresh = refresh;
        vm.editSighting = editSighting;
        vm.openDatePicker = openDatePicker;

        vm.sightings = undefined;
        vm.fromDate = vm.toDate = vm.fromDateMax = vm.toDateMax = $filter('date')(new Date(), 'yyyy-MM-dd');
        vm.fromDateIsOpen = vm.toDateIsOpen = false;

        vm.datepickerOptions = {
            showWeeks: false,
            startingDay: 1
        };

        activate();

        function activate() {
            var user = Authentication.getAuthenticatedUser();
            if (user) {
                refresh();
                $interval(refresh, 10000);

                $scope.$watch('vm.fromDate', function () {
                    vm.fromDate = $filter('date')(vm.fromDate, 'yyyy-MM-dd');
                    refreshSightingsWithFromDate();
                });

                $scope.$watch('vm.toDate', function () {
                    vm.toDate = $filter('date')(vm.toDate, 'yyyy-MM-dd');
                    vm.fromDateMax = vm.toDate;
                    if (vm.toDate < vm.fromDate) {
                        vm.fromDate = vm.toDate;
                    }
                    refresh();
                });
            }
            else {
                $location.url('/');
            }
        }

        function refresh() {
            if (vm.toDate) {
                Sightings.list(vm.toDate + ' 23:59:59').then(successFn, errorFn);
            }

            function successFn(data, status, headers, config) {
                vm.sightings = data.data;
                refreshSightingsWithFromDate();
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.statusText;
            }
        }

        function editSighting(sighting) {
            var dlg = dialogs.create('static/templates/sightings/sighting.html', 'SightingController as vm', sighting, 'sm');
            dlg.result.then(function (editedSighting) {
                for (var k in editedSighting) { //Copy the object attributes to the currently displayed on the table
                    place[k] = editedSighting[k];
                }
            });
        }

        function refreshSightingsWithFromDate() {
            if (vm.sightings) {
                for (var i = 0; i < vm.sightings.length; i++) {
                    vm.sightings[i].wasRecentlySeen = vm.sightings[i].last_seen_at > vm.fromDate;
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