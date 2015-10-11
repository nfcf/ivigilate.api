(function () {
    'use strict';

    angular
        .module('ivigilate.limits.controllers')
        .controller('AddEditLimitController', AddEditLimitController);

    AddEditLimitController.$inject = ['$location', '$scope', '$timeout', '$modalInstance', 'data',
        'Authentication', 'Beacons', 'Events', 'Limits'];

    function AddEditLimitController($location, $scope, $timeout, $modalInstance, data,
                                    Authentication, Beacons, Events, Limits) {
        var vm = this;
        vm.openDateTimePicker = openDateTimePicker;
        vm.cancel = cancel;
        vm.destroy = destroy;
        vm.save = save;

        vm.error = undefined;
        vm.title = undefined;

        vm.limit = undefined;

        vm.notification_categories = ['Success', 'Info', 'Warning', 'Error'];
        vm.action_notification_title = undefined;
        vm.action_notification_category = 'Info';
        vm.action_notification_timeout = undefined;
        vm.action_notification_message = undefined;
        vm.action_sms_recipients = undefined;
        vm.action_sms_message = undefined;
        vm.action_email_recipients = undefined;
        vm.action_email_subject = undefined;
        vm.action_email_body = undefined;

        vm.actions_index = 0;

        vm.events = [];
        vm.events_selected = [];
        vm.beacons = [];
        vm.beacons_selected = [];

        vm.is_edit = data !== null;

        vm.occurrence_date_start_limit_is_open = false;
        vm.occurrence_date_end_limit_is_open = false;
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
            var now = new Date();
            var user = Authentication.getAuthenticatedUser();
            if (user) {
                if (vm.is_edit) {
                    vm.title = 'Limit';
                    vm.limit = data;

                    vm.limit.occurrence_date_start_limit = new Date(vm.limit.occurrence_date_start_limit);
                    if (!!vm.limit.occurrence_date_end_limit) {
                        vm.limit.occurrence_date_end_limit = new Date(vm.limit.occurrence_date_end_limit);
                    }
                    if (vm.limit.occurrence_count_limit < 0) vm.limit.occurrence_count_limit = undefined;

                    if (!!vm.limit.metadata) {
                        var metadata = JSON.parse(vm.limit.metadata);
                        vm.limit.consider_each_beacon_separately = !!metadata.consider_each_beacon_separately;

                        for (var i = 0; i < metadata.actions.length; i++) {  // Required for the REST serializer
                            if (metadata.actions[i].type == 'NOTIFICATION') {
                                vm.action_notification_title = metadata.actions[i].title;
                                vm.action_notification_category = metadata.actions[i].category;
                                vm.action_notification_timeout = metadata.actions[i].timeout;
                                vm.action_notification_message = metadata.actions[i].message;
                            } else if (metadata.actions[i].type == 'SMS') {
                                vm.action_sms_recipients = metadata.actions[i].recipients;
                                vm.action_sms_message = metadata.actions[i].message;
                            } else if (metadata.actions[i].type == 'EMAIL') {
                                vm.action_email_recipients = metadata.actions[i].recipients;
                                vm.action_email_subject = metadata.actions[i].subject;
                                vm.action_email_body = metadata.actions[i].body;
                            }
                        }
                    }
                } else {
                    vm.title = 'New Limit';
                    vm.limit = { 'is_active': true, 'occurrence_date_start_limit': new Date() };
                }

                Events.list().then(eventsSuccessFn, errorFn);
                Beacons.list().then(beaconsSuccessFn, errorFn);
            }
            else {
                $location.url('/');
            }

            function eventsSuccessFn(data, status, headers, config) {
                vm.events = data.data;
                if (vm.is_edit) vm.events_selected = vm.limit.events;
            }

            function beaconsSuccessFn(data, status, headers, config) {
                vm.beacons = data.data;
                if (vm.is_edit) vm.beacons_selected = vm.limit.beacons;
            }

            function errorFn(data, status, headers, config) {
                vm.error = 'Failed to get Objects with error: ' + JSON.stringify(data.data);
            }
        }

        function openDateTimePicker($event, isOpen) {
            $event.preventDefault();
            $event.stopPropagation();
            vm[isOpen] = !vm[isOpen];
        }

        function save() {
            $scope.$broadcast('show-errors-check-validity');

            if (vm.form.$valid) {
                var metadata = {};
                metadata.consider_each_beacon_separately = vm.limit.consider_each_beacon_separately;
                metadata.actions = [];

                if (vm.action_notification_message) {
                    metadata.actions.push({
                        'type': 'NOTIFICATION',
                        'title': vm.action_notification_title,
                        'category': vm.action_notification_category,
                        'timeout': vm.action_notification_timeout,
                        'message': vm.action_notification_message
                    });
                }
                if (vm.action_sms_recipients && vm.action_sms_message) {
                    metadata.actions.push({
                        'type': 'SMS',
                        'recipients': vm.action_sms_recipients,
                        'message': vm.action_sms_message
                    });
                }
                if (vm.action_email_recipients && vm.action_email_subject) {
                    metadata.actions.push({
                        'type': 'EMAIL',
                        'recipients': vm.action_email_recipients,
                        'subject': vm.action_email_subject,
                        'body': vm.action_email_body
                    });
                }
                vm.limit.metadata = JSON.stringify(metadata);

                var limitToSend = JSON.parse(JSON.stringify(vm.limit));
                limitToSend.events = [];
                for (var i = 0; i < vm.events_selected.length; i++) {  // Required for the REST serializer
                    limitToSend.events.push(vm.events_selected[i].id);
                }
                limitToSend.beacons = [];
                for (var i = 0; i < vm.beacons_selected.length; i++) {  // Required for the REST serializer
                    limitToSend.beacons.push(vm.beacons_selected[i].id);
                }

                if (vm.is_edit) {
                    Limits.update(limitToSend).then(successFn, errorFn);
                } else {
                    Limits.add(limitToSend).then(successFn, errorFn);
                }
            } else {
                vm.error = 'There are invalid fields in the form.';
            }

            function successFn(data, status, headers, config) {
                vm.limit.events = vm.events_selected;
                vm.limit.beacons = vm.beacons_selected;

                vm.limit.occurrence_date_start_limit = vm.limit.occurrence_date_start_limit.toISOString();
                if (!!vm.limit.occurrence_date_end_limit) {
                    vm.limit.occurrence_date_end_limit = vm.limit.occurrence_date_end_limit.toISOString();
                }
                $modalInstance.close(vm.limit);
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
            }
        }

        function destroy() {
            Limits.destroy(vm.limit);
            $modalInstance.close(null);
        }

        function cancel() {
            $modalInstance.dismiss();
        }
    }
})();