(function () {
    'use strict';

    angular
        .module('ivigilate.places.controllers')
        .controller('PlaceController', PlaceController);

    PlaceController.$inject = ['$location', '$scope', 'Authentication', 'Places'];

    function PlaceController($location, $scope, Authentication, Places) {
        var vm = this;
        vm.update = update;

        vm.place = undefined;
        vm.map = undefined;
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

        activate();

        function activate() {
            var user = Authentication.getAuthenticatedUser();
            if (user) {
                Places.get(1).then(placesSuccessFn, placesErroFn);
            }

            function placesSuccessFn(data, status, headers, config) {
                vm.place = data.data;
                vm.map = {
                    center: {
                        latitude: vm.place.location.split(",")[0],
                        longitude: vm.place.location.split(",")[1]
                    }, zoom: 8
                };
                vm.marker.coords.latitude = vm.map.center.latitude;
                vm.marker.coords.longitude = vm.map.center.longitude;
            }

            function placesErroFn(data, status, headers, config) {
                $location.url('/');
            }
        }

        function update() {
            Places.update(vm.place);
        }
    }
})();