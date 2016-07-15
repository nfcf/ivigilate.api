(function () {
    'use strict';

    angular
        .module('ivigilate.beacons.services')
        .factory('Beacons', Beacons);

    Beacons.$inject = ['$http', '$upload'];

    function Beacons($http, $upload) {

        var Beacons = {
            destroy: destroy,
            get: get,
            list: list,
            update: update
        };
        return Beacons;

        /////////////////////

        function destroy(beacon) {
            return $http.delete('/api/v1/beacons/' + beacon.id + '/');
        }

        function get(id) {
            return $http.get('/api/v1/beacons/' + id + '/');
        }

        function list() {
            return $http.get('/api/v1/beacons/');
        }

        function update(beacon, image) {
            var beaconToSend = JSON.parse(JSON.stringify(beacon));
            beaconToSend.photo = undefined;
            beaconToSend.unauthorized_events = [];
            if (!!beacon.unauthorized_events) {
                for (var i = 0; i < beacon.unauthorized_events.length; i++) {  // Required for the REST serializer
                    beaconToSend.unauthorized_events.push(beacon.unauthorized_events[i].id);
                }
            }

            if (!!image) {
                return $upload.upload({
                    url: '/api/v1/beacons/' + beaconToSend.id + '/',
                    method: 'PUT',
                    fields: beaconToSend,
                    file: image,
                    fileFormDataName: 'photo'
                });
            } else {
                return $http.put('/api/v1/beacons/' + beaconToSend.id + '/', beaconToSend);
            }
        }
    }
})();