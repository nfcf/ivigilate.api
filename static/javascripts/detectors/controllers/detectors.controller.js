(function () {
    'use strict';

    angular
        .module('ivigilate.detectors.controllers')
        .controller('DetectorsController', DetectorsController);

    DetectorsController.$inject = ['$location', '$scope', 'Authentication', 'Detectors', 'Payments', 'dialogs'];

    function DetectorsController($location, $scope, Authentication, Detectors, Payments, dialogs) {
        var vm = this;
        vm.refresh = refresh;
        vm.editDetector = editDetector;
        vm.updateDetectorState = updateDetectorState;

        vm.error = undefined;

        vm.detectors = undefined;

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
            Detectors.list().then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                vm.detectors = data.data;
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
            }
        }

        function editDetector(detector) {
            var dlg = dialogs.create('static/templates/detectors/editdetector.html', 'EditDetectorController as vm', detector, {'size': 'lg'});
            dlg.result.then(function (editedDetector) {
                refresh()
            });
        }

        function updateDetectorState(detector) {
            Detectors.update(detector).then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                // Do nothing...
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
                detector.is_active = !detector.is_active;
            }
        }
    }
})();