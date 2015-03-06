(function () {
    'use strict';

    angular
        .module('ivigilate.places.controllers')
        .controller('PlacesController', PlacesController);

    PlacesController.$inject = ['$location', '$scope', 'Authentication', 'Places', 'dialogs'];

    function PlacesController($location, $scope, Authentication, Places, dialogs) {
        var vm = this;
        vm.refresh = refresh;
        vm.editPlace = editPlace;

        vm.places = undefined;

        activate();

        function activate() {
            var user = Authentication.getAuthenticatedUser();
            if (user) {
                refresh();
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
                vm.error = data.data.status + ": " + data.data.message;
                setTimeout($location.url('/'), 5);
            }
        }

        function editPlace(place) {
            var dlg = dialogs.create('static/templates/places/place.html', 'PlaceController as vm', place, 'lg');
            dlg.result.then(function(editedPlace) {
                place = editedPlace;
            });

            //$location.url('/places/' + place.id);
        }
    }
})();