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
        vm.current_marker = [];

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
                        'lng': vm.sighting.location.coordinates[0],
                        'lat': vm.sighting.location.coordinates[1],
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
            vm.current_marker.push ([vm.map.markers['m']['lat'], vm.map.markers['m']['lng']]);
            zoomToFit();
            //set up map custom controls
            leafletData.getMap('viewGpsMap').then(function (map) {
                L.easyButton('fa-arrows', function () {
                    zoomToFit();
                }).addTo(map);

            });
        }

        function cancel() {
            $modalInstance.dismiss('Cancel');
        }

        function zoomToFit() {
           if(!vm.map.markers){
                vm.current_marker.push([vm.map.maxbounds.northEast.lat, vm.map.maxbounds.northEast.lng],
                    [vm.map.maxbounds.southWest.lat, vm.map.maxbounds.southWest.lng]);
            }
            vm.mapBounds = new L.latLngBounds(vm.current_marker);
            leafletData.getMap('viewGpsMap').then(function (map) {
                map.fitBounds(vm.mapBounds, {padding: [50, 50]});
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