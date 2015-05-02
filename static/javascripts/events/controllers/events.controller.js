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
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
            }
        }

        function editEvent(event) {
            var dlg = dialogs.create('static/templates/events/edit_event.html', 'EditEventController as vm', event, 'lg');
            dlg.result.then(function (editedPlaceEvent) {
                for (var k in editedPlaceEvent) { //Copy the object attributes to the currently displayed on the table
                    event[k] = editedPlaceEvent[k];
                }
            });
        }
    }
})();