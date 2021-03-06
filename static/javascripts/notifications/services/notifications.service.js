(function () {
    'use strict';

    angular
        .module('ivigilate.notifications.services')
        .factory('Notifications', Notifications);

    Notifications.$inject = ['$http', 'toastr', 'ngAudio'];

    function Notifications($http, toastr, ngAudio) {

        var sound = ngAudio.load("static/sounds/alarm.mp3"); // returns NgAudioObject
        sound.loop = true;

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
                var isPlaying = false;
                if (!!notifications) {
                    for (var i = 0; i < notifications.length; i++) {
                        try {
                            var notification = notifications[i];
                            var metadata = JSON.parse(notification.metadata);
                            toastr[metadata.category.toLowerCase()](metadata.message, metadata.title, {
                                onHidden: (function (notification) {
                                    return function (clicked) {
                                        closeNotification(notification);
                                    }
                                }(notification)),
                                timeOut: !!metadata.timeout ? metadata.timeout * 1000 : 0,
                                extendedTimeOut: !!metadata.timeout ? metadata.timeout * 1000 : 0
                            });
                            if (!isPlaying && sound.paused) {
                                isPlaying = true;
                                sound.play();
                                if (!!metadata.timeout) {
                                    setTimeout(function () {
                                        sound.pause();
                                    }, metadata.timeout * 1000);
                                }
                            }
                        } catch (ex) {
                            console.log('Failed to parse notification data with error: ' + ex.message);
                        }
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
            sound.pause();
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