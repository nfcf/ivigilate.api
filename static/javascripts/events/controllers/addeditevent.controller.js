(function () {
    'use strict';

    angular
        .module('ivigilate.events.controllers')
        .controller('AddEditEventController', AddEditEventController);

    AddEditEventController.$inject = ['$location', '$scope', '$timeout', '$modalInstance', 'data',
        'Authentication', 'Beacons', 'Detectors', 'Events'];

    function AddEditEventController($location, $scope, $timeout, $modalInstance, data,
                                    Authentication, Beacons, Detectors, Events) {
        var vm = this;
        vm.cancel = cancel;
        vm.destroy = destroy;
        vm.save = save;

        vm.error = undefined;
        vm.title = undefined;

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
        vm.schedule_timezone_offset = undefined;

        vm.notification_categories = ['Success', 'Info', 'Warning', 'Error'];
        vm.actions_index = 0;

        vm.events = [];
        vm.nullEventOption = {"name": "-- Don't care --"};
        vm.beacons = [];
        vm.beacons_selected = [];
        vm.detectors = [];
        vm.detectors_selected = [];

        vm.is_edit = data !== null;

        activate();

        function activate() {
            var now = new Date();
            var user = Authentication.getAuthenticatedUser();
            if (user) {
                if (vm.is_edit) {
                    vm.title = 'Event';
                    vm.event = data;
                    vm.event.schedule_timezone_offset = Math.abs(now.getTimezoneOffset());

                    vm.schedule_monday = vm.event.schedule_days_of_week & Math.pow(2, 0);
                    vm.schedule_tuesday = vm.event.schedule_days_of_week & Math.pow(2, 1);
                    vm.schedule_wednesday = vm.event.schedule_days_of_week & Math.pow(2, 2);
                    vm.schedule_thursday = vm.event.schedule_days_of_week & Math.pow(2, 3);
                    vm.schedule_friday = vm.event.schedule_days_of_week & Math.pow(2, 4);
                    vm.schedule_saturday = vm.event.schedule_days_of_week & Math.pow(2, 5);
                    vm.schedule_sunday = vm.event.schedule_days_of_week & Math.pow(2, 6);

                    var start_time_parts = vm.event.schedule_start_time.split(':');
                    vm.schedule_start_time = new Date(now.getFullYear(), now.getMonth(), now.getDate(), start_time_parts[0], start_time_parts[1]);
                    var end_time_parts = vm.event.schedule_end_time.split(':');
                    vm.schedule_end_time = new Date(now.getFullYear(), now.getMonth(), now.getDate(), end_time_parts[0], end_time_parts[1]);

                    if (!!vm.event.metadata) {
                        var metadata = JSON.parse(vm.event.metadata);

                        vm.event.metadata_object = metadata;
                        vm.event.metadata_object.action_notification_category = 'Info'; // Default value
                        for (var i = 0; i < metadata.actions.length; i++) {  // Required for the REST serializer
                            if (metadata.actions[i].type == 'NOTIFICATION') {
                                vm.event.metadata_object.action_notification_title = metadata.actions[i].title;
                                vm.event.metadata_object.action_notification_category = metadata.actions[i].category;
                                vm.event.metadata_object.action_notification_timeout = metadata.actions[i].timeout;
                                vm.event.metadata_object.action_notification_message = metadata.actions[i].message;
                            } else if (metadata.actions[i].type == 'SMS') {
                                vm.event.metadata_object.action_sms_recipients = metadata.actions[i].recipients;
                                vm.event.metadata_object.action_sms_message = metadata.actions[i].message;
                            } else if (metadata.actions[i].type == 'EMAIL') {
                                vm.event.metadata_object.action_email_recipients = metadata.actions[i].recipients;
                                vm.event.metadata_object.action_email_subject = metadata.actions[i].subject;
                                vm.event.metadata_object.action_email_body = metadata.actions[i].body;
                            } else if (metadata.actions[i].type == 'REST') {
                                vm.event.metadata_object.action_rest_uri = metadata.actions[i].uri;
                                vm.event.metadata_object.action_rest_method = metadata.actions[i].method;
                                vm.event.metadata_object.action_rest_body = metadata.actions[i].body;
                            }
                        }
                    }
                } else {
                    vm.title = 'New Event';
                    vm.event = {'is_active': true, 'schedule_timezone_offset': Math.abs(now.getTimezoneOffset()),
                                'metadata_object': {
                                    'action_notification_category': 'Info',
                                    'sighting_duration_in_seconds': 0,
                                    'sighting_has_battery_below': 100,
                                    'sighting_dormant_period_in_seconds': 0,
                                    'sighting_arrival_rssi': 0,
                                    'sighting_departure_rssi': -99
                                }};

                    vm.schedule_start_time = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0);
                    vm.schedule_end_time = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59);
                }

                Beacons.list().then(beaconsSuccessFn, errorFn);
                Detectors.list().then(detectorsSuccessFn, errorFn);
                Events.list().then(eventsSuccessFn, errorFn);
            }
            else {
                $location.url('/');
            }

            function beaconsSuccessFn(data, status, headers, config) {
                vm.beacons = data.data;
                if (vm.is_edit) vm.beacons_selected = vm.event.beacons;
            }

            function detectorsSuccessFn(data, status, headers, config) {
                vm.detectors = data.data;
                if (vm.is_edit) vm.detectors_selected = vm.event.detectors;
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
            $scope.$broadcast('show-errors-check-validity');

            if (vm.form.$valid) {
                vm.event.schedule_days_of_week = vm.schedule_monday + vm.schedule_tuesday + vm.schedule_wednesday +
                vm.schedule_thursday + vm.schedule_friday + vm.schedule_saturday +
                vm.schedule_sunday;

                vm.event.schedule_start_time = pad('00', vm.schedule_start_time.getHours(), true) + ':' +
                pad('00', vm.schedule_start_time.getMinutes(), true) + ':00';
                vm.event.schedule_end_time = pad('00', vm.schedule_end_time.getHours(), true) + ':' +
                pad('00', vm.schedule_end_time.getMinutes(), true) + ':59';

                if (vm.event.metadata_object.sighting_previous_event) {
                    vm.event.metadata_object.sighting_previous_event = vm.event.metadata_object.sighting_previous_event.id;
                }
                vm.event.metadata_object.actions = [];
                if (vm.event.metadata_object.action_notification_message) {
                    vm.event.metadata_object.actions.push({
                        'type': 'NOTIFICATION',
                        'title': vm.event.metadata_object.action_notification_title,
                        'category': vm.event.metadata_object.action_notification_category,
                        'timeout': vm.event.metadata_object.action_notification_timeout,
                        'message': vm.event.metadata_object.action_notification_message
                    });
                }
                vm.event.metadata_object.action_notification_title = undefined;
                vm.event.metadata_object.action_notification_category = undefined;
                vm.event.metadata_object.action_notification_timeout = undefined;
                vm.event.metadata_object.action_notification_message = undefined;

                if (vm.event.metadata_object.action_sms_recipients && vm.event.metadata_object.action_sms_message) {
                    vm.event.metadata_object.actions.push({
                        'type': 'SMS',
                        'recipients': vm.event.metadata_object.action_sms_recipients,
                        'message': vm.event.metadata_object.action_sms_message
                    });
                }
                vm.event.metadata_object.action_sms_recipients = undefined;
                vm.event.metadata_object.action_sms_message = undefined;

                if (vm.event.metadata_object.action_email_recipients && vm.event.metadata_object.action_email_subject) {
                    vm.event.metadata_object.actions.push({
                        'type': 'EMAIL',
                        'recipients': vm.event.metadata_object.action_email_recipients,
                        'subject': vm.event.metadata_object.action_email_subject,
                        'body': vm.event.metadata_object.action_email_body
                    });
                }
                vm.event.metadata_object.action_email_recipients = undefined;
                vm.event.metadata_object.action_email_subject = undefined;
                vm.event.metadata_object.action_email_body = undefined;

                if (vm.event.metadata_object.action_rest_uri && vm.event.metadata_object.action_rest_method) {
                    vm.event.metadata_object.actions.push({
                        'type': 'REST',
                        'uri': vm.event.metadata_object.action_rest_uri,
                        'method': vm.event.metadata_object.action_rest_method,
                        'body': vm.event.metadata_object.action_rest_body
                    });
                }
                vm.event.metadata_object.action_rest_uri = undefined;
                vm.event.metadata_object.action_rest_method = undefined;
                vm.event.metadata_object.action_rest_body = undefined;

                vm.event.metadata = JSON.stringify(vm.event.metadata_object);

                var eventToSend = JSON.parse(JSON.stringify(vm.event));
                eventToSend.metadata_object = undefined;
                eventToSend.beacons = [];
                for (var i = 0; i < vm.beacons_selected.length; i++) {  // Required for the REST serializer
                    eventToSend.beacons.push(vm.beacons_selected[i].id);
                }
                eventToSend.detectors = [];
                for (var i = 0; i < vm.detectors_selected.length; i++) {  // Required for the REST serializer
                    eventToSend.detectors.push(vm.detectors_selected[i].id);
                }

                if (vm.is_edit) {
                    Events.update(eventToSend).then(successFn, errorFn);
                } else {
                    Events.add(eventToSend).then(successFn, errorFn);
                }
            } else {
                vm.error = 'There are invalid fields in the form.';
            }

            function successFn(data, status, headers, config) {
                vm.event.beacons = vm.beacons_selected;
                vm.event.detectors = vm.detectors_selected;
                $modalInstance.close(vm.event);
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
            }
        }

        function destroy() {
            Events.destroy(vm.event);
            $modalInstance.close(null);
        }

        function cancel() {
            $modalInstance.dismiss();
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
         description: 'Triggered as soon as a movable gets out of the configured place(s) detector\'s range.',
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