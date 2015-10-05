(function () {
    'use strict';

    angular
        .module('ivigilate.limits.controllers')
        .controller('LimitsController', LimitsController);

    LimitsController.$inject = ['$location', '$scope', 'Authentication', 'Limits', 'Payments', 'dialogs'];

    function LimitsController($location, $scope, Authentication, Limits, Payments, dialogs) {
        var vm = this;
        vm.refresh = refresh;
        vm.addLimit = addLimit;
        vm.editLimit = editLimit;
        vm.updateLimitState = updateLimitState;

        vm.limits = undefined;

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
            Limits.list().then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                vm.limits = data.data;
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
            }
        }

        function addLimit() {
            var dlg = dialogs.create('static/templates/limits/addeditlimit.html', 'AddEditLimitController as vm', null, {'size': 'lg'});
            dlg.result.then(function (newLimit) {
                refresh();
            });
        }

        function editLimit(limit) {
            var dlg = dialogs.create('static/templates/limits/addeditlimit.html', 'AddEditLimitController as vm', event, {'size': 'lg'});
            dlg.result.then(function (editedLimit) {
                if (editedLimit) {
                    for (var k in editedLimit) { //Copy the object attributes to the currently displayed on the table
                        limit[k] = editedLimit[k];
                    }
                } else {
                    var index = vm.limits.indexOf(limit);
                    if (index >= 0) vm.limits.splice(index, 1);
                }
            });
        }

        function updateLimitState(limit) {
            var limitToSend = JSON.parse(JSON.stringify(limit));
            limitToSend.event = limitToSend.event.id;
            limitToSend.beacon = limitToSend.beacon.id;
            Limits.update(limitToSend).then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                // Do nothing...
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
                limit.is_active = !limit.is_active;
            }
        }
    }
})();