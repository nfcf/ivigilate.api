(function () {
    'use strict';

    angular
        .module('ivigilate.places.controllers')
        .controller('PlaceController', PlaceController);

    PlaceController.$inject = ['$location', '$scope', '$timeout', '$modalInstance', 'data', 'Authentication', 'Places', 'uiGmapGoogleMapApi'];

    function PlaceController($location, $scope, $timeout, $modalInstance, data, Authentication, Places, uiGmapGoogleMapApi) {
        var vm = this;
        vm.cancel = cancel;
        vm.save = save;

        vm.error = undefined;
        vm.place = undefined;
        vm.map = undefined;
        vm.showMap = false;
        vm.marker = {
            id: 1,
            coords: {
                latitude: 0,
                longitude: 0
            },
            options: {draggable: true},
            events: {
                dragend: function (marker, eventName, args) {
                    vm.place.location = marker.getPosition().lat() + "," + marker.getPosition().lng();
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
                        vm.map.center.zoom = 15;

                        vm.marker.coords.latitude = vm.map.center.latitude;
                        vm.marker.coords.longitude = vm.map.center.longitude;
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
                        populateDialog(data, user);
                        vm.showMap = true;
                    }, 250);
                });
            }
            else {
                $location.url('/');
            }
        }

        function populateDialog(data, user) {
            vm.place = data;

            vm.map = {
                center: {
                    latitude: vm.place.location ? vm.place.location.split(",")[0] : "34.698986644",
                    longitude: vm.place.location ? vm.place.location.split(",")[1] : "-40.70744491"
                }, zoom: 8
            };
            vm.marker.coords.latitude = vm.map.center.latitude;
            vm.marker.coords.longitude = vm.map.center.longitude;
        }

        function save() {
            Places.update(vm.place).then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                $modalInstance.close(vm.place);
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