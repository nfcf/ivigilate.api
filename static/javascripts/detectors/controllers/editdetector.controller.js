(function () {
    'use strict';

    angular
        .module('ivigilate.detectors.controllers')
        .controller('EditDetectorController', EditDetectorController);

    EditDetectorController.$inject = ['$location', '$scope', '$timeout', '$modalInstance', 'data', 'Authentication', 'Detectors', 'uiGmapGoogleMapApi'];

    function EditDetectorController($location, $scope, $timeout, $modalInstance, data, Authentication, Detectors, uiGmapGoogleMapApi) {
        var vm = this;
        vm.fileChanged = fileChanged;
        vm.cancel = cancel;
        vm.save = save;

        vm.error = undefined;
        vm.detector = undefined;
        vm.imagePreview = undefined;
        vm.imageToUpload = undefined;
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
                    vm.detector.location.coordinates = [marker.getPosition().lng(), marker.getPosition().lat()];
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

                        vm.detector.location.coordinates = [vm.marker.coords.longitude, vm.marker.coords.latitude];
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
            vm.detector = data;
            vm.imagePreview = vm.detector.photo;

            $scope.$watch('vm.detector.type', function () {
                vm.showMap = vm.detector.type == 'F';
            }, true);

            if (!vm.detector.location) {
                vm.detector.location = {
                    'type': 'Point',
                    'coordinates': [-40.70744491, 34.698986644] //Defaults to the middle of the ocean
                };
            }

            vm.map = {
                center: {
                    longitude: vm.detector.location.coordinates[0],
                    latitude: vm.detector.location.coordinates[1]
                },
                zoom: vm.defaultZoomLevel
            };
            vm.marker.coords.latitude = vm.map.center.latitude;
            vm.marker.coords.longitude = vm.map.center.longitude;
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
    }
})();