(function () {
    'use strict';

    angular
        .module('ivigilate.places.controllers')
        .controller('PlacesController', PlacesController);

    PlacesController.$inject = ['$location', '$scope', 'Authentication', 'Places'];

    function PlacesController($location, $scope, Authentication, Places) {
        var vm = this;
        vm.refresh = refresh;

        vm.places = undefined;

        activate();

        function activate() {
            var user = Authentication.getAuthenticatedUser();
            if (user) {
                refresh();
            }
        }

        function refresh() {
            Places.list().then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                vm.places = data.data;
            }

            function errorFn(data, status, headers, config) {
                $location.url('/');
            }
        }
    }
})();