(function () {
    'use strict';

    angular
        .module('ivigilate.places.controllers')
        .controller('EditSightingController', EditSightingController);

    EditSightingController.$inject = ['$location', '$scope', '$timeout', '$modalInstance', 'data',
        'Authentication', 'Movables', 'Sightings', 'Events'];

    function EditSightingController($location, $scope, $timeout, $modalInstance, data,
                                    Authentication, Movables, Sightings, Events) {
        var vm = this;
        vm.fileChanged = fileChanged;
        vm.cancel = cancel;
        vm.save = save;

        vm.error = undefined;
        vm.events = [];
        vm.sighting = undefined;
        vm.imagePreview = undefined;
        vm.imageToUpload = undefined;

        activate();

        function activate() {
            var user = Authentication.getAuthenticatedUser();
            if (user) {
                vm.sighting = data;
                vm.imagePreview = vm.sighting.movable.photo;
                Events.list().then(eventsSuccessFn, eventsErrorFn);
            }
            else {
                $location.url('/');
            }

            function eventsSuccessFn(data, status, headers, config) {
                vm.events = data.data;
            }

            function eventsErrorFn(data, status, headers, config) {
                vm.error = 'Failed to get Places with error: ' + JSON.stringify(data.data);
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
            var movableToSend = JSON.parse(JSON.stringify(vm.sighting.movable));
            for (var i = 0; i < vm.sighting.movable.events.length; i++) {  // Required for the REST serializer
                movableToSend.events[i] = vm.sighting.movable.events[i].id;
            }
            movableToSend.photo = undefined;
            Movables.update(movableToSend, vm.imageToUpload).then(movableSuccessFn, movableErrorFn, movableProgressFn);

            function movableSuccessFn(data, status, headers, config) {
                vm.sighting.movable = vm.sighting.movable.id;  // Required for the REST serializer
                vm.sighting.place = vm.sighting.place.id;  // Required for the REST serializer
                Sightings.update(vm.sighting).then(sightingSuccessFn, sightingErrorFn);

                function sightingSuccessFn(data, status, headers, config) {
                    $modalInstance.close(vm.sighting);
                }

                function sightingErrorFn(data, status, headers, config) {
                    vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
                }
            }

            function movableErrorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
            }

            function movableProgressFn(evt) {
                //Do nothing for now...
            }
        }

        function cancel() {
            $modalInstance.dismiss('Cancel');
        }

    }
})();