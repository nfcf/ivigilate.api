(function () {
    'use strict';

    angular
        .module('ivigilate.places.controllers')
        .controller('EditSightingController', EditSightingController);

    EditSightingController.$inject = ['$location', '$scope', '$timeout', '$modalInstance', 'data',
        'Authentication', 'Beacons', 'Sightings', 'Events'];

    function EditSightingController($location, $scope, $timeout, $modalInstance, data,
                                    Authentication, Beacons, Sightings, Events) {
        var vm = this;
        vm.fileChanged = fileChanged;
        vm.cancel = cancel;
        vm.save = save;

        vm.error = undefined;
        vm.events = [];
        vm.events_selected = [];
        vm.sighting = undefined;
        vm.imagePreview = undefined;
        vm.imageToUpload = undefined;

        activate();

        function activate() {
            var user = Authentication.getAuthenticatedUser();
            if (user) {
                vm.sighting = data;
                vm.imagePreview = vm.sighting.beacon.photo;

                Events.list().then(eventsSuccessFn, eventsErrorFn);
            }
            else {
                $location.url('/');
            }

            function eventsSuccessFn(data, status, headers, config) {
                vm.events = data.data;
                vm.events_selected = vm.sighting.beacon.events;
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
            vm.sighting.beacon.events = vm.events_selected;

            var beaconToSend = JSON.parse(JSON.stringify(vm.sighting.beacon));
            beaconToSend.events = [];
            for (var i = 0; i < vm.sighting.beacon.events.length; i++) {  // Required for the REST serializer
                beaconToSend.events.push(vm.sighting.beacon.events[i].id);
            }
            beaconToSend.photo = undefined;
            Beacons.update(beaconToSend, vm.imageToUpload).then(beaconSuccessFn, beaconErrorFn, beaconProgressFn);

            function beaconSuccessFn(data, status, headers, config) {
                vm.sighting.beacon = vm.sighting.beacon.id;  // Required for the REST serializer
                vm.sighting.place = !!vm.sighting.place ? vm.sighting.place.id : null;  // Required for the REST serializer
                vm.sighting.user = !!vm.sighting.user ? vm.sighting.user.id : null;  // Required for the REST serializer
                Sightings.update(vm.sighting).then(sightingSuccessFn, sightingErrorFn);

                function sightingSuccessFn(data, status, headers, config) {
                    $modalInstance.close(vm.sighting);
                }

                function sightingErrorFn(data, status, headers, config) {
                    vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
                }
            }

            function beaconErrorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
            }

            function beaconProgressFn(evt) {
                //Do nothing for now...
            }
        }

        function cancel() {
            $modalInstance.dismiss('Cancel');
        }

    }
})();