(function () {
    'use strict';

    angular
        .module('ivigilate.beacons.controllers')
        .controller('EditBeaconController', EditBeaconController);

    EditBeaconController.$inject = ['$location', '$scope', '$timeout', '$modalInstance', 'data', 'Authentication', 'Beacons', 'Events', 'leafletData'];

    function EditBeaconController($location, $scope, $timeout, $modalInstance, data, Authentication, Beacons, Events, leafletData) {
        var vm = this;
        vm.fileChanged = fileChanged;
        vm.cancel = cancel;
        vm.save = save;
        vm.resizeMap = resizeMap;
        vm.zoomToFit = zoomToFit;

        vm.error = undefined;
        vm.beacon = undefined;
        vm.imagePreview = undefined;
        vm.imageToUpload = undefined;
        vm.events = [];
        vm.events_selected = [];
        vm.map = undefined;
        vm.showMap = false;
        vm.current_markers = [];

        var searchControl = new L.Control.Search({
            url: 'http://nominatim.openstreetmap.org/search?format=json&q={s}',
            jsonpParam: 'json_callback',
            propertyName: 'display_name',
            propertyLoc: ['lat', 'lon'],
            autoCollapse: true,
            autoType: false,
            minLength: 2
        });
        searchControl.on('search_locationfound', function (e) {
            vm.map.markers['m']['lng'] = e.latlng['lng'];
            vm.map.markers['m']['lat'] = e.latlng['lat'];
            vm.beacon.location.coordinates = [vm.map.markers['m']['lng'], vm.map.markers['m']['lat']];
        });

        leafletData.getMap('editBeaconMap').then(function (map) {
            map.addControl(searchControl);
        });


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
            vm.beacon = data;
            vm.imagePreview = vm.beacon.photo;

            $scope.$watch('vm.beacon.type', function () {
                vm.showMap = vm.beacon.type == 'F';
            }, true);

            if (!vm.beacon.location) {
                vm.beacon.location = {
                    'type': 'Point',
                    'coordinates': [-40.70744491, 34.698986644] //Defaults to the middle of the ocean
                };
            }

            vm.map = {
                defaults: {
                    scrollWheelZoom: false
                },
                maxbounds: {'northEast': {'lat': -60, 'lng': -120}, 'southWest': {'lat': 60, 'lng': 120}},
                markers: {
                    'm': {
                        'lng': vm.beacon.location.coordinates[0],
                        'lat': vm.beacon.location.coordinates[1],
                        'message': vm.beacon['type'] + " " + vm.beacon['name'] + " with ID: " + vm.beacon['uid'],
                        'icon': {
                            'type': 'vectorMarker',
                            'icon': 'map-marker',
                            'markerColor': '#00c6d2'
                        }
                    }
                }
            };
            resizeMap();
            vm.current_markers.push ([vm.map.markers['m']['lat'], vm.map.markers['m']['lng']]);
            zoomToFit();
            //set up map custom controls
            leafletData.getMap('editBeaconMap').then(function (map) {
                L.easyButton('fa-arrows', function () {
                    zoomToFit();
                }).addTo(map);

            });

            Events.list().then(eventsSuccessFn, eventsErrorFn);

            function eventsSuccessFn(data, status, headers, config) {
                vm.events = data.data;
                vm.events_selected = vm.beacon.unauthorized_events;
            }

            function eventsErrorFn(data, status, headers, config) {
                vm.error = 'Failed to get Detectors with error: ' + JSON.stringify(data.data);
            }
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
                vm.beacon.unauthorized_events = vm.events_selected;
                Beacons.update(vm.beacon, vm.imageToUpload).then(successFn, errorFn, progressFn);
            } else {
                vm.error = 'There are invalid fields in the form.';
            }

            function successFn(data, status, headers, config) {
                $modalInstance.close(vm.sighting);
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
            }

            function progressFn(evt) {
                //Do nothing for now...
            }
        }

        function cancel() {
            $modalInstance.dismiss('Cancel');
        }

        function zoomToFit() {
            if(!vm.map.markers){
                vm.current_markers.push([vm.map.maxbounds.northEast.lat, vm.map.maxbounds.northEast.lng],
                    [vm.map.maxbounds.southWest.lat, vm.map.maxbounds.southWest.lng]);
            }
            vm.mapBounds = new L.latLngBounds(vm.current_markers);
            leafletData.getMap('editBeaconMap').then(function (map) {
                map.fitBounds(vm.mapBounds, {padding: [50, 50]});
            });
        }

        function resizeMap() {
            leafletData.getMap('editBeaconMap').then(function (map) {
                setTimeout(function () {
                    map.invalidateSize();
                    map.options.minZoom = 1;
                }, 500);
            });
        }
    }

})();