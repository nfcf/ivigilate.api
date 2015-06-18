(function () {
    'use strict';

    angular
        .module('ivigilate.beacons.controllers')
        .controller('BeaconsController', BeaconsController);

    BeaconsController.$inject = ['$location', 'Authentication', 'Beacons', 'Payments', 'dialogs'];

    function BeaconsController($location, Authentication, Beacons, Payments, dialogs) {
        var vm = this;
        vm.refresh = refresh;
        vm.editBeacon = editBeacon;
        vm.updateBeaconState = updateBeaconState;

        vm.error = undefined;

        vm.beacons = undefined;

        activate();

        function activate() {
            var user = Authentication.getAuthenticatedUser();
            if (user) {
                Payments.checkLicense(user).then(function () {
                    refresh();
                });
            }
            else {
                $location.url('/');
            }
        }

        function refresh() {
            Beacons.list().then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                vm.beacons = data.data;
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
            }
        }

        function editBeacon(beacon) {
            var dlg = dialogs.create('static/templates/beacons/editbeacon.html', 'EditBeaconController as vm', beacon, {'size': 'lg'});
            dlg.result.then(function (editedBeacon) {
                /*for (var k in editedBeacon) { //Copy the object attributes to the currently displayed on the table
                    beacon[k] = editedBeacon[k];
                }*/
                refresh();
            });
        }

        function updateBeaconState(beacon) {
            Beacons.update(beacon).then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                // Do nothing...
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
                beacon.is_active = !beacon.is_active;
            }
        }
    }
})();