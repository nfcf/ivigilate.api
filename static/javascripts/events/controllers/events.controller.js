(function () {
    'use strict';

    angular
        .module('ivigilate.events.controllers')
        .controller('EventsController', EventsController);

    EventsController.$inject = ['$location', '$scope', 'Authentication', 'Events', 'dialogs'];

    function EventsController($location, $scope, Authentication, Events, dialogs) {
        var vm = this;
        vm.refresh = refresh;
        vm.editEvent = editEvent;
        vm.updateEventState = updateEventState;

        vm.events = undefined;

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
            Events.list().then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                vm.events = data.data;

                for (var i = 0; i < vm.events.length; i++) {
                    vm.events[i].schedule_days_of_week_string = '';
                    if (vm.events[i].schedule_days_of_week & Math.pow(2, 0) > 0) {
                        vm.events[i].schedule_days_of_week_string += 'Mon,';
                    }
                    if (vm.events[i].schedule_days_of_week & Math.pow(2, 1) > 0) {
                        vm.events[i].schedule_days_of_week_string += 'Tue,';
                    }
                    if (vm.events[i].schedule_days_of_week & Math.pow(2, 2) > 0) {
                        vm.events[i].schedule_days_of_week_string += 'Wed,';
                    }
                    if (vm.events[i].schedule_days_of_week & Math.pow(2, 3) > 0) {
                        vm.events[i].schedule_days_of_week_string += 'Thu,';
                    }
                    if (vm.events[i].schedule_days_of_week & Math.pow(2, 4) > 0) {
                        vm.events[i].schedule_days_of_week_string += 'Fri,';
                    }
                    if (vm.events[i].schedule_days_of_week & Math.pow(2, 5) > 0) {
                        vm.events[i].schedule_days_of_week_string += 'Sat,';
                    }
                    if (vm.events[i].schedule_days_of_week & Math.pow(2, 6) > 0) {
                        vm.events[i].schedule_days_of_week_string += 'Sun';
                    }
                }
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
            }
        }

        function editEvent(event) {
            var dlg = dialogs.create('static/templates/events/editevent.html', 'EditEventController as vm', event, 'lg');
            dlg.result.then(function (editedPlaceEvent) {
                for (var k in editedPlaceEvent) { //Copy the object attributes to the currently displayed on the table
                    event[k] = editedPlaceEvent[k];
                }
            });
        }

        function updateEventState(event) {
            Events.update(event).then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                // Do nothing...
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
                event.is_active = !event.is_active;
            }
        }
    }
})();