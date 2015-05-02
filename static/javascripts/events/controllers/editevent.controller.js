(function () {
    'use strict';

    angular
        .module('ivigilate.events.controllers')
        .controller('EditEventController', EditEventController);

    EditEventController.$inject = ['$location', '$scope', '$timeout', '$modalInstance', 'data',
                                    'Authentication', 'Events'];

    function EditEventController($location, $scope, $timeout, $modalInstance, data,
                                 Authentication, Events) {
        var vm = this;
        vm.cancel = cancel;
        vm.save = save;

        vm.error = undefined;
        vm.event = undefined;

        activate();

        function activate() {
            var user = Authentication.getAuthenticatedUser();
            if (user) {
                vm.event = data;
            }
            else {
                $location.url('/');
            }
        }

        function save() {
            Events.update(vm.event).then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                $modalInstance.close(vm.event);
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