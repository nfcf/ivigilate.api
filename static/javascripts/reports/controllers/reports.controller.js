(function () {
    'use strict';

    angular
        .module('ivigilate.reports.controllers')
        .controller('ReportsController', ReportsController);

    ReportsController.$inject = ['$location', '$scope', '$filter', '$timeout', 'Authentication', 'Reports'];

    function ReportsController($location, $scope, $filter, $timeout, Authentication, Reports) {
        var vm = this;
        vm.openDateTimePicker = openDateTimePicker;
        vm.generate = generate;

        vm.success = undefined;
        vm.error = undefined;

        vm.filter = {};
        vm.from_date_is_open = false;
        vm.to_date_is_open = false;
        vm.max_date = $filter('date')(new Date(), 'yyyy-MM-dd');
        vm.date_options = {
            showWeeks: false,
            startingDay: 1
        };
        vm.time_options = {
            showMeridian: false,
            minuteStep: 5
        };

        activate();

        function activate() {
            var user = Authentication.getAuthenticatedUser();
            if (user) {
                var now =  new Date();

                vm.filter.report_type = 'EO';
                vm.filter.from_date = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0);
                vm.filter.to_date = new Date(now.getFullYear(), now.getMonth(), now.getDate(), now.getHours(), Math.ceil(now.getMinutes() / 5) * 5, 59);
            }
            else {
                $location.url('/');
            }
        }

        function openDateTimePicker($event, isOpen) {
            $event.preventDefault();
            $event.stopPropagation();
            vm[isOpen] = !vm[isOpen];
        }

        function generate() {
            $scope.$broadcast('show-errors-check-validity');

            if (vm.form.$valid) {
                Reports.get(vm.filter);
            } else {
                vm.error = 'There are invalid fields in the form.';
                vm.success = null;
            }
        }
    }
})();