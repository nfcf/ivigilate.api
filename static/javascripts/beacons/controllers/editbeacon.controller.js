(function () {
    'use strict';

    angular
        .module('ivigilate.beacons.controllers')
        .controller('EditBeaconController', EditBeaconController);

    EditBeaconController.$inject = ['$location', '$scope', '$timeout', '$modalInstance', 'data', 'Authentication', 'Beacons', 'Events', 'uiGmapGoogleMapApi'];

    function EditBeaconController($location, $scope, $timeout, $modalInstance, data, Authentication, Beacons, Events, uiGmapGoogleMapApi) {
        var vm = this;
        vm.fileChanged = fileChanged;
        vm.cancel = cancel;
        vm.save = save;

        vm.error = undefined;
        vm.beacon = undefined;
        vm.imagePreview = undefined;
        vm.imageToUpload = undefined;
        vm.events = [];
        vm.events_selected = [];
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
                    vm.beacon.location.coordinates = [marker.getPosition().lng(), marker.getPosition().lat()];
                }
            }
        };
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

                        vm.beacon.location.coordinates = [vm.marker.coords.longitude, vm.marker.coords.latitude];
                    }
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
                center: {
                    longitude: vm.beacon.location.coordinates[0],
                    latitude: vm.beacon.location.coordinates[1]
                },
                zoom: vm.defaultZoomLevel
            };
            vm.marker.coords.latitude = vm.map.center.latitude;
            vm.marker.coords.longitude = vm.map.center.longitude;

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
    }
})();