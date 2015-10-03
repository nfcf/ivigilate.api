(function () {
    'use strict';

    angular
        .module('ivigilate.notifications.services')
        .factory('Notifications', Notifications);

    Notifications.$inject = ['$http', 'toastr'];

    function Notifications($http, toastr) {

        var Notifications = {
            checkForNotifications: checkForNotifications,
            closeNotification: closeNotification
        };
        return Notifications;

        /////////////////////

        function checkForNotifications() {
            $http.get('/api/v1/notifications/').then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                var notifications = data.data;
                if (!!notifications) {
                    for (var i = 0; i < notifications.length; i++) {
                        var notification = notifications[i];
                        var metadata = JSON.parse(notification.metadata);
                        toastr[metadata.category](metadata.message, metadata.title, {
                            onHidden: (function (notification) {
                                return function (clicked) {
                                    closeNotification(notification);
                                }}(notification))
                        });
                    }
                }
            }

            function errorFn(data, status, headers, config) {
                console.log('Failed to get notification data with error: ' +
                    data.status != 500 ? JSON.stringify(data.data) : data.statusText);
            }
        }

        function closeNotification(notification) {
            notification.is_active = false;
            return $http.put('/api/v1/notifications/' + notification.id + '/', notification).then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                //Hurray! do nothing...
            }

            function errorFn(data, status, headers, config) {
                console.log('Failed to update (close) notification with error: ' +
                    data.status != 500 ? JSON.stringify(data.data) : data.statusText);
            }
        }
    }
})();