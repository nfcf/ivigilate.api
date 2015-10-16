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
        vm.actions_index = 0;

        vm.events = [];
        vm.events_selected = [];
        vm.beacons = [];
        vm.beacons_selected = [];

        vm.is_edit = data !== null;

        vm.start_date_is_open = false;
        vm.occurrence_date_limit_is_open = false;
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
                    vm.limit.start_date = new Date(vm.limit.start_date + ' 00:00:00');

                    if (!!vm.limit.metadata) {
                        var metadata = JSON.parse(vm.limit.metadata);

                        vm.limit.metadata_object = {};
                        vm.limit.metadata_object.occurrence_date_limit = !!metadata.occurrence_date_limit ?
                                                                        new Date(metadata.occurrence_date_limit) : undefined;
                        vm.limit.metadata_object.occurrence_count_limit = metadata.occurrence_count_limit >= 0 ?
                                                                        metadata.occurrence_count_limit : undefined;
                        vm.limit.metadata_object.consider_each_beacon_separately = !!metadata.consider_each_beacon_separately;

                        vm.limit.metadata_object.action_notification_category = 'Info'; // Default value
                        for (var i = 0; i < metadata.actions.length; i++) {  // Required for the REST serializer
                            if (metadata.actions[i].type == 'NOTIFICATION') {
                                vm.limit.metadata_object.action_notification_title = metadata.actions[i].title;
                                vm.limit.metadata_object.action_notification_category = metadata.actions[i].category;
                                vm.limit.metadata_object.action_notification_timeout = metadata.actions[i].timeout;
                                vm.limit.metadata_object.action_notification_message = metadata.actions[i].message;
                            } else if (metadata.actions[i].type == 'SMS') {
                                vm.limit.metadata_object.action_sms_recipients = metadata.actions[i].recipients;
                                vm.limit.metadata_object.action_sms_message = metadata.actions[i].message;
                            } else if (metadata.actions[i].type == 'EMAIL') {
                                vm.limit.metadata_object.action_email_recipients = metadata.actions[i].recipients;
                                vm.limit.metadata_object.action_email_subject = metadata.actions[i].subject;
                                vm.limit.metadata_object.action_email_body = metadata.actions[i].body;
                            } else if (metadata.actions[i].type == 'REST') {
                                vm.limit.metadata_object.action_rest_uri = metadata.actions[i].uri;
                                vm.limit.metadata_object.action_rest_method = metadata.actions[i].method;
                                vm.limit.metadata_object.action_rest_body = metadata.actions[i].body;
                            }
                        }
                    }
                } else {
                    vm.title = 'New Limit';
                    vm.limit = { 'is_active': true,
                                'start_date': new Date(now.getFullYear(), now.getMonth(), now.getDate()),
                                'metadata_object': { 'action_notification_category': 'Info' } };
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
                vm.limit.metadata_object.actions = [];

                if (vm.limit.metadata_object.action_notification_message) {
                    vm.limit.metadata_object.actions.push({
                        'type': 'NOTIFICATION',
                        'title': vm.limit.metadata_object.action_notification_title,
                        'category': vm.limit.metadata_object.action_notification_category,
                        'timeout': vm.limit.metadata_object.action_notification_timeout,
                        'message': vm.limit.metadata_object.action_notification_message
                    });
                }
                vm.limit.metadata_object.action_notification_title = undefined;
                vm.limit.metadata_object.action_notification_category = undefined;
                vm.limit.metadata_object.action_notification_timeout = undefined;
                vm.limit.metadata_object.action_notification_message = undefined;

                if (vm.limit.metadata_object.action_sms_recipients && vm.limit.metadata_object.action_sms_message) {
                    vm.limit.metadata_object.actions.push({
                        'type': 'SMS',
                        'recipients': vm.limit.metadata_object.action_sms_recipients,
                        'message': vm.limit.metadata_object.action_sms_message
                    });
                }
                vm.limit.metadata_object.action_sms_recipients = undefined;
                vm.limit.metadata_object.action_sms_message = undefined;

                if (vm.limit.metadata_object.action_email_recipients && vm.limit.metadata_object.action_email_subject) {
                    vm.limit.metadata_object.actions.push({
                        'type': 'EMAIL',
                        'recipients': vm.limit.metadata_object.action_email_recipients,
                        'subject': vm.limit.metadata_object.action_email_subject,
                        'body': vm.limit.metadata_object.action_email_body
                    });
                }
                vm.limit.metadata_object.action_email_recipients = undefined;
                vm.limit.metadata_object.action_email_subject = undefined;
                vm.limit.metadata_object.action_email_body = undefined;

                if (vm.limit.metadata_object.action_rest_uri && vm.limit.metadata_object.action_rest_method) {
                    vm.limit.metadata_object.actions.push({
                        'type': 'REST',
                        'uri': vm.limit.metadata_object.action_rest_uri,
                        'method': vm.limit.metadata_object.action_rest_method,
                        'body': vm.limit.metadata_object.action_rest_body
                    });
                }
                vm.limit.metadata_object.action_rest_uri = undefined;
                vm.limit.metadata_object.action_rest_method = undefined;
                vm.limit.metadata_object.action_rest_body = undefined;

                vm.limit.metadata = JSON.stringify(vm.limit.metadata_object);

                var limitToSend = JSON.parse(JSON.stringify(vm.limit));
                limitToSend.metadata_object = undefined;
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