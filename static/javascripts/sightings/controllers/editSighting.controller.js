(function () {
    'use strict';

    angular
        .module('ivigilate.places.controllers')
        .controller('EditSightingController', EditSightingController);

    EditSightingController.$inject = ['$location', '$scope', '$modalInstance', 'data', 'Authentication', 'Movables', 'Sightings'];

    function EditSightingController($location, $scope, $modalInstance, data, Authentication, Movables, Sightings) {
        var vm = this;
        vm.fileChanged = fileChanged;
        vm.cancel = cancel;
        vm.save = save;

        vm.error = undefined;
        vm.sighting = undefined;
        vm.image = undefined;

        activate();

        function activate() {
            var user = Authentication.getAuthenticatedUser();
            if (user) {
                vm.sighting = data;
                vm.image = vm.sighting.movable.photo;
            }
            else {
                $location.url('/');
            }
        }

        function fileChanged(files) {
            if (files && files[0]) {
                var fileReader = new FileReader();
                fileReader.onload = function (e) {
                    $scope.$apply(function () {
                        vm.image = fileReader.result;
                    });
                };
                fileReader.readAsDataURL(files[0]);
            } else {
                vm.image = null;
            }

        }

        function save() {
            Movables.upload(vm.sighting.movable, vm.image).then(successFn, errorFn, progressFn);

            function successFn(data, status, headers, config) {
                vm.sightings.movable.photo = data;
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
            }

            function progressFn(evt) {
                //Do nothing for now...
            }

            Movables.update(vm.sighting.movable);

            Sightings.add(vm.sighting).then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                $modalInstance.close(vm.sighting);
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