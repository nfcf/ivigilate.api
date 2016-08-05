(function () {
    'use strict';

    angular
        .module('ivigilate.sightings.controllers')
        .controller('ViewGpsController', ViewGpsController);

    ViewGpsController.$inject = ['$location', '$scope', '$timeout', '$modalInstance', 'data', 'Authentication', 'Sightings', 'leafletData'];

    function ViewGpsController($location, $scope, $timeout, $modalInstance, data, Authentication, Detectors, leafletData) {
        var vm = this;
        vm.cancel = cancel;
        vm.resizeMap = resizeMap;
        vm.zoomToFit = zoomToFit;


        vm.error = undefined;
        vm.sighting = undefined;
        vm.map = undefined;
        vm.showMap = false;
        vm.defaultZoomLevel = 15;

        activate();

        function activate() {
            var user = Authentication.getAuthenticatedUser();
            if (user) {
                populateDialog(data);
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
                    lng: vm.sighting.location.coordinates[0],
                    lat: vm.sighting.location.coordinates[1],
                    zoom: 10
                },
                defaults: {
                    scrollWheelZoom: false
                },
                maxbounds: {'northEast': {'lat': -60, 'lng': -120}, 'southWest': {'lat': 60, 'lng': 120}},
                markers: {
                    'm': {
                        'lng': parseFloat(vm.sighting.location.coordinates[0]),
                        'lat': parseFloat(vm.sighting.location.coordinates[1]),
                        'message': vm.sighting['detector']['type'] + " " + vm.sighting['detector']['name'] + " with ID: " + vm.sighting['detector']['uid'],
                        'icon': {
                            'type': 'vectorMarker',
                            'icon': 'map-marker',
                            'markerColor': '#00c6d2'
                        }
                    }
                }
            };
            resizeMap();
        }

        function cancel() {
            $modalInstance.dismiss('Cancel');
        }

        function zoomToFit() {
            vm.mapBounds = new L.latLngBounds([vm.map.markers.m1['lat'], vm.map.markers.m1['lng']]);
            leafletData.getMap('viewGpsMap').then(function (map) {
                map.fitBounds(vm.mapBounds, {padding: [30, 30]});
            });
        }

        function resizeMap() {
            leafletData.getMap('viewGpsMap').then(function (map) {
                setTimeout(function () {
                    map.invalidateSize();
                    map.options.minZoom = 1;
                }, 500);
            });
        }

    }
})();