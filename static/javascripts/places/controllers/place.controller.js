(function () {
    'use strict';

    angular
        .module('ivigilate.places.controllers')
        .controller('PlaceController', PlaceController);

    PlaceController.$inject = ['$location', '$scope', '$timeout', '$routeParams', 'Authentication', 'Places'];

    function PlaceController($location, $scope, $timeout, $routeParams, Authentication, Places) {
        var vm = this;
        vm.update = update;

        vm.success = undefined;
        vm.error = undefined;
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
                Places.get($routeParams.place_id).then(successFn, errorFn);
            }
            else {
                $location.url('/');
            }

            function successFn(data, status, headers, config) {
                vm.place = data.data;

                if (user.account == vm.place.account) { // Check if place belongs to account
                    vm.map = {
                        center: {
                            latitude: vm.place.location.split(",")[0],
                            longitude: vm.place.location.split(",")[1]
                        }, zoom: 8
                    };
                    vm.marker.coords.latitude = vm.map.center.latitude;
                    vm.marker.coords.longitude = vm.map.center.longitude;
                } else {
                    vm.place = undefined;
                    vm.error = "You don't have permissions to edit this place's information."
                }
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.data.status + ": " + data.data.message;
                $timeout(function(){ $location.url('/'); }, 5000);
            }
        }

        function update() {
            Places.update(vm.place);
        }
    }
})();