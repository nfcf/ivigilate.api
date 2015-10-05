(function () {
    'use strict';

    angular
        .module('ivigilate.events.controllers')
        .controller('EventsController', EventsController);

    EventsController.$inject = ['$location', '$scope', 'Authentication', 'Events', 'Payments', 'dialogs'];

    function EventsController($location, $scope, Authentication, Events, Payments, dialogs) {
        var vm = this;
        vm.refresh = refresh;
        vm.addEvent = addEvent;
        vm.editEvent = editEvent;
        vm.updateEventState = updateEventState;

        vm.events = undefined;

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
            Events.list().then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                vm.events = data.data;

                generateDaysOfWeekString(vm.events);
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
            }
        }

        function addEvent() {
            var dlg = dialogs.create('static/templates/events/addeditevent.html', 'AddEditEventController as vm', null, {'size': 'lg'});
            dlg.result.then(function (newEvent) {
                refresh();
            });
        }

        function editEvent(event) {
            var dlg = dialogs.create('static/templates/events/addeditevent.html', 'AddEditEventController as vm', event, {'size': 'lg'});
            dlg.result.then(function (editedEvent) {
                if (editedEvent) {
                    for (var k in editedEvent) { //Copy the object attributes to the currently displayed on the table
                        event[k] = editedEvent[k];
                    }
                    generateDaysOfWeekString(vm.events);
                } else {
                    var index = vm.events.indexOf(event);
                    if (index >= 0) vm.events.splice(index, 1);
                }
            });
        }

        function updateEventState(event) {
            var eventToSend = JSON.parse(JSON.stringify(event));
            eventToSend.sighting_previous_event = eventToSend.sighting_previous_event.id;
            eventToSend.beacons = null;
            eventToSend.detectors = null;
            Events.update(eventToSend).then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                // Do nothing...
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
                event.is_active = !event.is_active;
            }
        }

        function generateDaysOfWeekString(events) {
            for (var i = 0; i < events.length; i++) {
                events[i].schedule_days_of_week_string = '';
                if ((events[i].schedule_days_of_week & Math.pow(2, 0)) > 0) {
                    events[i].schedule_days_of_week_string += 'Mon,';
                }
                if ((events[i].schedule_days_of_week & Math.pow(2, 1)) > 0) {
                    events[i].schedule_days_of_week_string += 'Tue,';
                }
                if ((events[i].schedule_days_of_week & Math.pow(2, 2)) > 0) {
                    events[i].schedule_days_of_week_string += 'Wed,';
                }
                if ((events[i].schedule_days_of_week & Math.pow(2, 3)) > 0) {
                    events[i].schedule_days_of_week_string += 'Thu,';
                }
                if ((events[i].schedule_days_of_week & Math.pow(2, 4)) > 0) {
                    events[i].schedule_days_of_week_string += 'Fri,';
                }
                if ((events[i].schedule_days_of_week & Math.pow(2, 5)) > 0) {
                    events[i].schedule_days_of_week_string += 'Sat,';
                }
                if ((events[i].schedule_days_of_week & Math.pow(2, 6)) > 0) {
                    events[i].schedule_days_of_week_string += 'Sun';
                }
            }
        }
    }
})();