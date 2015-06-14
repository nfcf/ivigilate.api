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

        function update(beacon) {
            return $http.put('/api/v1/beacons/' + beacon.id + '/', beacon);
        }

        function update(beacon, image) {
            return $upload.upload({
                url: '/api/v1/beacons/' + beacon.id + '/',
                method: 'PUT',
                fields: beacon,
                file: image,
                fileFormDataName: 'photo'
            });
        }
    }
})();