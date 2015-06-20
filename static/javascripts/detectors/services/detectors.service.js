(function () {
    'use strict';

    angular
        .module('ivigilate.detectors.services')
        .factory('Detectors', Detectors);

    Detectors.$inject = ['$http'];

    function Detectors($http) {

        var Detectors = {
            destroy: destroy,
            get: get,
            list: list,
            update: update
        };
        return Detectors;

        /////////////////////

        function destroy(detector) {
            return $http.delete('/api/v1/detectors/' + detector.id + '/');
        }

        function get(id) {
            return $http.get('/api/v1/detectors/' + id + '/');
        }

        function list() {
            return $http.get('/api/v1/detectors/');
        }

        function update(detector) {
            return $http.put('/api/v1/detectors/' + detector.id + '/', detector);
        }
    }
})();