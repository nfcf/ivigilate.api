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
        vm.schedule_monday = 1;
        vm.schedule_tuesday = 2;
        vm.schedule_wednesday = 4;
        vm.schedule_thursday = 8;
        vm.schedule_friday = 16;
        vm.schedule_saturday = 32;
        vm.schedule_sunday = 64;
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

                vm.schedule_monday = vm.event.schedule_days_of_week & Math.pow(2, 0);
                vm.schedule_tuesday = vm.event.schedule_days_of_week & Math.pow(2, 1);
                vm.schedule_wednesday = vm.event.schedule_days_of_week & Math.pow(2, 2);
                vm.schedule_thursday = vm.event.schedule_days_of_week & Math.pow(2, 3);
                vm.schedule_friday = vm.event.schedule_days_of_week & Math.pow(2, 4);
                vm.schedule_saturday = vm.event.schedule_days_of_week & Math.pow(2, 5);
                vm.schedule_sunday = vm.event.schedule_days_of_week & Math.pow(2, 6);

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
            vm.event.schedule_days_of_week = vm.schedule_monday + vm.schedule_tuesday + vm.schedule_wednesday +
                                             vm.schedule_thursday + vm.schedule_friday + vm.schedule_saturday +
                                             vm.schedule_sunday;
            vm.event.schedule_start_time = pad('00', vm.schedule_start_time.getHours(), true) + ':' + pad('00', vm.schedule_start_time.getMinutes(), true) + ':00';
            vm.event.schedule_end_time = pad('00', vm.schedule_end_time.getHours(), true) + ':' + pad('00', vm.schedule_end_time.getMinutes(), true) + ':59';

            var eventToSend = JSON.parse(JSON.stringify(vm.event));
            eventToSend.movables = [];
            for (var i = 0; i < vm.movables_selected.length; i++) {  // Required for the REST serializer
                eventToSend.movables.push(vm.movables_selected[i].id);
            }
            eventToSend.places = [];
            for (var i = 0; i < vm.places_selected.length; i++) {  // Required for the REST serializer
                eventToSend.places.push(vm.places_selected[i].id);
            }

            eventToSend.sighting_previous_event = vm.event.sighting_previous_event.id;
            Events.update(eventToSend).then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                vm.event.movables = vm.movables_selected;
                vm.event.places = vm.places_selected;
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