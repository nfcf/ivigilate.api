(function () {
    'use strict';

    angular
        .module('ivigilate.detectors.controllers')
        .controller('EditDetectorController', EditDetectorController);

    EditDetectorController.$inject = ['$location', '$scope', '$timeout', '$modalInstance', 'data', 'Authentication', 'Detectors', 'leafletData'];

    function EditDetectorController($location, $scope, $timeout, $modalInstance, data, Authentication, Detectors, leafletData) {
        var vm = this;
        vm.fileChanged = fileChanged;
        vm.cancel = cancel;
        vm.save = save;
        vm.resizeMap = resizeMap;
        vm.zoomToFit = zoomToFit;

        vm.error = undefined;
        vm.detector = undefined;
        vm.imagePreview = undefined;
        vm.imageToUpload = undefined;
        vm.map = undefined;
        vm.showMap = false;
        //todo:this has to work with new search
        var searchControl = new L.Control.Search({
            url: 'http://nominatim.openstreetmap.org/search?format=json&q={s}',
            jsonpParam: 'json_callback',
            propertyName: 'display_name',
            propertyLoc: ['lat', 'lon'],
            markerLocation: true,
            autoCollapse: true,
            autoType: false,
            minLength: 2
        });

        searchControl.on('search_locationfound', function (e) {
            vm.coords = e.latlng;
        });


        leafletData.getMap('editDetectorMap').then(function (map) {
            map.addControl(searchControl);
        });


        vm.coords = [];

        vm.searchbox = {
            template: 'searchbox.tpl.html',
            events: {
                places_changed: function (searchBox) {
                    var places = searchBox.getPlaces();
                    if (places && places.length > 0) {
                        vm.map.center.latitude = places[0].geometry.location.lat();
                        vm.map.center.longitude = places[0].geometry.location.lng();
                        vm.map.center.zoom = vm.defaultZoomLevel;

                        vm.marker.coords.latitude = vm.map.center.latitude;
                        vm.marker.coords.longitude = vm.map.center.longitude;

                        vm.detector.location.coordinates = [vm.marker.coords.longitude, vm.marker.coords.latitude];
                    }
                }
            }
        };

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
            vm.detector = data;
            vm.imagePreview = vm.detector.photo;

            $scope.$watch('vm.detector.type', function () {
                vm.showMap = vm.detector.type == 'F';
            }, true);

            $scope.$watch('vm.coords', function () {
                if(vm.coords.length === 0){
                    return;
                }
                 vm.map.markers['m']['lat'] = vm.coords['lat'];
                 vm.map.markers['m']['lng'] = vm.coords['lng'];
                 zoomToFit();
            }, true);

            if (!vm.detector.location) {
                vm.detector.location = {
                    'type': 'Point',
                    'coordinates': [-40.70744491, 34.698986644] //Defaults to the middle of the ocean
                };
            }
            vm.map = {
                center: {
                    lng: vm.detector.location.coordinates[0],
                    lat: vm.detector.location.coordinates[1],
                    zoom: 10
                },
                defaults: {
                    scrollWheelZoom: false
                },
                maxbounds: {'northEast': {'lat': -60, 'lng': -120}, 'southWest': {'lat': 60, 'lng': 120}},
                markers: {
                    'm': {
                        'lng': vm.detector.location.coordinates[0],
                        'lat': vm.detector.location.coordinates[1],
                        'message': vm.detector['type'] + " " + vm.detector['name'] + " with ID: " + vm.detector['uid'],
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

        function fileChanged(files) {
            if (files && files[0]) {
                var fileReader = new FileReader();
                fileReader.onload = function (e) {
                    $scope.$apply(function () {
                        vm.imageToUpload = files[0];
                        $timeout(function () {
                            vm.imagePreview = fileReader.result;
                        }, 250);
                    });
                };
                fileReader.readAsDataURL(files[0]);
            } else {
                vm.imagePreview = null;
            }
        }

        function save() {
            $scope.$broadcast('show-errors-check-validity');

            if (vm.form.$valid) {
                Detectors.update(vm.detector, vm.imageToUpload).then(successFn, errorFn);
            } else {
                vm.error = 'There are invalid fields in the form.';
            }

            function successFn(data, status, headers, config) {
                $modalInstance.close(vm.detector);
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
            }
        }

        function cancel() {
            $modalInstance.dismiss('Cancel');
        }

        function zoomToFit() {
            vm.mapBounds = new L.latLngBounds([vm.map.markers.m1['lat'], vm.map.markers.m1['lng']]);
            leafletData.getMap('editDetectorMap').then(function (map) {
                map.fitBounds(vm.mapBounds, {padding: [30, 30]});
            });
        }

        function resizeMap() {
            leafletData.getMap('editDetectorMap').then(function (map) {
                setTimeout(function () {
                    map.invalidateSize();
                    map.options.minZoom = 1;
                }, 500);
            });
        }

    }
})();