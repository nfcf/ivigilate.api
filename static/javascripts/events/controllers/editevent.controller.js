(function () {
    'use strict';

    angular
        .module('ivigilate.events.controllers')
        .controller('EditEventController', EditEventController);

    EditEventController.$inject = ['$location', '$scope', '$timeout', '$modalInstance', 'data',
        'Authentication', 'Movables', 'Places', 'Events'];

    function EditEventController($location, $scope, $timeout, $modalInstance, data,
                                 Authentication, Movables, Places, Events) {
        var vm = this;
        vm.cancel = cancel;
        vm.save = save;

        vm.error = undefined;

        vm.event = undefined;
        vm.schedule_monday = false;
        vm.schedule_tuesday = false;
        vm.schedule_wednesday = false;
        vm.schedule_thursday = false;
        vm.schedule_friday = false;
        vm.schedule_saturday = false;
        vm.schedule_sunday = false;
        vm.schedule_start_time = undefined;
        vm.schedule_end_time = undefined;

        vm.events = [];
        vm.nullEventOption = {"name": "-- Don't care --"};
        vm.movables = [];
        vm.movables_selected = [];
        vm.places = [];
        vm.places_selected = [];

        vm.actions_index = 0;

        activate();

        function activate() {
            var user = Authentication.getAuthenticatedUser();
            if (user) {
                vm.event = data;

                if (vm.event.schedule_days_of_week & Math.pow(2, 0) > 0) {
                    vm.schedule_monday = true;
                }
                if (vm.event.schedule_days_of_week & Math.pow(2, 1) > 0) {
                    vm.schedule_tuesday = true;
                }
                if (vm.event.schedule_days_of_week & Math.pow(2, 2) > 0) {
                    vm.schedule_wednesday = true;
                }
                if (vm.event.schedule_days_of_week & Math.pow(2, 3) > 0) {
                    vm.schedule_thursday = true;
                }
                if (vm.event.schedule_days_of_week & Math.pow(2, 4) > 0) {
                    vm.schedule_friday = true;
                }
                if (vm.event.schedule_days_of_week & Math.pow(2, 5) > 0) {
                    vm.schedule_saturday = true;
                }
                if (vm.event.schedule_days_of_week & Math.pow(2, 6) > 0) {
                    vm.schedule_sunday = true;
                }
                var start_time_parts = vm.event.schedule_start_time.split(':');
                vm.schedule_start_time = new Date(0, 0, 0, start_time_parts[0], start_time_parts[1]);
                var end_time_parts = vm.event.schedule_end_time.split(':');
                vm.schedule_end_time = new Date(0, 0, 0, end_time_parts[0], end_time_parts[1]);

                Movables.list().then(movablesSuccessFn, errorFn);
                Places.list().then(placesSuccessFn, errorFn);
                Events.list().then(eventsSuccessFn, errorFn);
            }
            else {
                $location.url('/');
            }

            function movablesSuccessFn(data, status, headers, config) {
                vm.movables = data.data;
                vm.movables_selected = vm.event.movables;
            }

            function placesSuccessFn(data, status, headers, config) {
                vm.places = data.data;
                vm.places_selected = vm.event.places;
            }

            function eventsSuccessFn(data, status, headers, config) {
                vm.events = data.data;
                vm.events.splice(0, 0, vm.nullEventOption);
            }

            function errorFn(data, status, headers, config) {
                vm.error = 'Failed to get Objects with error: ' + JSON.stringify(data.data);
            }
        }

        function save() {
            vm.event.schedule_start_time = pad('00', vm.schedule_start_time.getHours(), true) + ':' + pad('00', vm.schedule_start_time.getMinutes(), true) + ':00';
            vm.event.schedule_end_time = pad('00', vm.schedule_end_time.getHours(), true) + ':' + pad('00', vm.schedule_end_time.getMinutes(), true) + ':59';

            var eventToSend = JSON.parse(JSON.stringify(vm.event));
            if (vm.event.sighting_previous_event_occurrence !== null) {
                eventToSend.sighting_previous_event_occurrence = vm.event.sighting_previous_event_occurrence.id;
            }
            Events.update(eventToSend).then(successFn, errorFn);

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

        function pad(pad, str, padLeft) {
            if (str == undefined) return pad;
            if (padLeft) {
                return (pad + str).slice(-pad.length);
            } else {
                return (str + pad).substring(0, pad.length);
            }
        }

        /*function populateEventTypes() {
         event_types.push({
         name: 'Gone out of sight',
         description: 'Triggered as soon as a movable gets out of the configured place(s) receiver\'s range.',
         sighting_is_current: false,
         sighting_duration_in_seconds: 5,
         sighting_has_battery_below: 100,
         sighting_has_comment: null,
         sighting_has_been_confirmed: null,
         sighting_previous_event_occurrence: null
         });
         event_types.push({
         name: 'Seen at place',
         description: 'Triggered immediately after a movable is seen at any of the configured places.',
         sighting_is_current: true,
         sighting_duration_in_seconds: 0,
         sighting_has_battery_below: 100,
         sighting_has_comment: null,
         sighting_has_been_confirmed: null,
         sighting_previous_event_occurrence: null
         });
         event_types.push({
         name: 'Same place for more than X minutes',
         description: 'Triggered if a movable stays in the same place for more than the configured time.',
         sighting_is_current: true,
         sighting_duration_in_seconds: 5,
         sighting_has_battery_below: 100,
         sighting_has_comment: null,
         sighting_has_been_confirmed: null,
         sighting_previous_event_occurrence: null
         });
         }*/
    }
})();