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
            beaconToSend.events = [];
            for (var i = 0; i < beacon.events.length; i++) {  // Required for the REST serializer
                beaconToSend.events.push(beacon.events[i].id);
            }

            if (!!image) {
                return $upload.upload({
                    url: '/api/v1/beacons/' + beacon.id + '/',
                    method: 'PUT',
                    fields: beacon,
                    file: image,
                    fileFormDataName: 'photo'
                });
            } else {

                return $http.put('/api/v1/beacons/' + beaconToSend.id + '/', beaconToSend);
            }
        }
    }
})();