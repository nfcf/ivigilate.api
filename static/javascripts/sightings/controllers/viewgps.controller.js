(function () {
    'use strict';

    angular
        .module('ivigilate.sightings.controllers')
        .controller('ViewGpsController', ViewGpsController);

    ViewGpsController.$inject = ['$location', '$scope', '$timeout', '$modalInstance', 'data', 'Authentication', 'Sightings', 'uiGmapGoogleMapApi'];

    function ViewGpsController($location, $scope, $timeout, $modalInstance, data, Authentication, Detectors, uiGmapGoogleMapApi) {
        var vm = this;
        vm.cancel = cancel;


        vm.error = undefined;
        vm.sighting = undefined;
        vm.map = undefined;
        vm.showMap = false;
        vm.defaultZoomLevel = 15;
        vm.marker = {
            id: 1,
            coords: {
                latitude: 0,
                longitude: 0
            },
            options: {draggable: true},
            events: {
                dragend: function (marker, eventName, args) {
                    vm.sighting.location.coordinates = [marker.getPosition().lng(), marker.getPosition().lat()];
                }
            }
        };

        activate();

        function activate() {
            var user = Authentication.getAuthenticatedUser();
            if (user) {
                uiGmapGoogleMapApi.then(function (maps) {
                    $timeout(function () {
                        populateDialog(data);
                        vm.showMap = true;
                    }, 250);
                });
            }
            else {
                $location.url('/');
            }
        }

        function populateDialog(data) {
            vm.sighting = data;


            $scope.$watch('vm.sighting.type', function () {
                vm.showMap = vm.sighting.type === 'GPS';
            }, true);

            if (!vm.sighting.location) {
                vm.sighting.location = {
                    'type': 'Point',
                    'coordinates': [-40.70744491, 34.698986644] //Defaults to the middle of the ocean
                };
            }

            vm.map = {
                center: {
                    longitude: vm.sighting.location.coordinates[0],
                    latitude: vm.sighting.location.coordinates[1]
                },
                zoom: vm.defaultZoomLevel
            };
            vm.marker.coords.latitude = vm.map.center.latitude;
            vm.marker.coords.longitude = vm.map.center.longitude;
        }
        function cancel() {
            $modalInstance.dismiss('Cancel');
        }
    }
})();