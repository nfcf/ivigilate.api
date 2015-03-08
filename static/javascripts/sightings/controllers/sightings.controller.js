(function () {
    'use strict';

    angular
        .module('ivigilate.sightings.controllers')
        .controller('SightingsController', SightingsController);

    SightingsController.$inject = ['$location', '$scope', 'Authentication', 'Sightings', 'dialogs'];

    function SightingsController($location, $scope, Authentication, Sightings, dialogs) {
        var vm = this;
        vm.refresh = refresh;
        vm.editSighting = editSighting;

        vm.sightings = undefined;

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
            Sightings.list().then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                vm.sightings = data.data;
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.statusText;
            }
        }

        function editSighting(sighting) {
            var dlg = dialogs.create('static/templates/sightings/sighting.html', 'SightingController as vm', sighting, 'sm');
            dlg.result.then(function (editedSighting) {
                for (var k in editedSighting) { //Copy the object attributes to the currently displayed on the table
                    place[k] = editedSighting[k];
                }
            });
        }
    }
})();