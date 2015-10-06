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
        vm.action_notification_message = undefined;
        vm.action_sms_recipients = undefined;
        vm.action_sms_message = undefined;
        vm.action_email_recipients = undefined;
        vm.action_email_subject = undefined;
        vm.action_email_body = undefined;

        vm.actions_index = 0;

        vm.events = [];
        vm.beacons = [];
        vm.nullBeaconOption = {"name": "-- Any Beacon --"};

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

                    if (!!vm.limit.metadata) {
                        var metadata = JSON.parse(vm.limit.metadata);
                        for (var i = 0; i < metadata.actions.length; i++) {  // Required for the REST serializer
                            if (metadata.actions[i].type == 'NOTIFICATION') {
                                vm.action_notification_title = metadata.actions[i].title;
                                vm.action_notification_category = metadata.actions[i].category;
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
                    vm.limit = { 'is_active': true };
                }

                Beacons.list().then(beaconsSuccessFn, errorFn);
                Events.list().then(eventsSuccessFn, errorFn);
            }
            else {
                $location.url('/');
            }

            function beaconsSuccessFn(data, status, headers, config) {
                vm.beacons = data.data;
                vm.beacons.splice(0, 0, vm.nullBeaconOption);
            }

            function eventsSuccessFn(data, status, headers, config) {
                vm.events = data.data;
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
                var metadata = {'actions': []};
                if (vm.action_notification_message) {
                    metadata.actions.push({
                        'type': 'NOTIFICATION',
                        'title': vm.action_notification_title,
                        'category': vm.action_notification_category,
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
                if (!!vm.limit.beacon) {
                    limitToSend.beacon = vm.limit.beacon.id;
                }
                if (!!vm.limit.event) {
                    limitToSend.event = vm.limit.event.id;
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

        function pad(pad, str, padLeft) {
            if (str == undefined) return pad;
            if (padLeft) {
                return (pad + str).slice(-pad.length);
            } else {
                return (str + pad).substring(0, pad.length);
            }
        }
    }
})();