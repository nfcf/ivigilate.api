(function () {
    'use strict';

    angular
        .module('ivigilate.places.controllers')
        .controller('PlacesController', PlacesController);

    PlacesController.$inject = ['$location', '$scope', 'Authentication', 'Places', 'Payments', 'dialogs'];

    function PlacesController($location, $scope, Authentication, Places, Payments, dialogs) {
        var vm = this;
        vm.refresh = refresh;
        vm.editPlace = editPlace;
        vm.updatePlaceState = updatePlaceState;

        vm.error = undefined;

        vm.places = undefined;

        activate();

        function activate() {
            var user = Authentication.getAuthenticatedUser();
            if (user) {
                Payments.checkLicense(user).then(function () { refresh(); });
            }
            else {
                $location.url('/');
            }
        }

        function refresh() {
            Places.list().then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                vm.places = data.data;
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
            }
        }

        function editPlace(place) {
            var dlg = dialogs.create('static/templates/places/editplace.html', 'EditPlaceController as vm', place, {'size': 'lg'});
            dlg.result.then(function (editedPlace) {
                for (var k in editedPlace) { //Copy the object attributes to the currently displayed on the table
                    place[k] = editedPlace[k];
                }
            });
        }

        function updatePlaceState(place) {
            Places.update(place).then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                // Do nothing...
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
                place.is_active = !place.is_active;
            }
        }
    }
})();