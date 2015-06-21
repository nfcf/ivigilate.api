(function () {
    'use strict';

    angular
        .module('ivigilate.detectors.services')
        .factory('Detectors', Detectors);

    Detectors.$inject = ['$http', '$upload'];

    function Detectors($http, $upload) {

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

        function update(detector, image) {
            var detectorToSend = JSON.parse(JSON.stringify(detector));
            detectorToSend.photo = undefined;

            if (!!image) {
                return $upload.upload({
                    url: '/api/v1/detectors/' + detectorToSend.id + '/',
                    method: 'PUT',
                    fields: detectorToSend,
                    file: image,
                    fileFormDataName: 'photo'
                });
            } else {
                return $http.put('/api/v1/detectors/' + detectorToSend.id + '/', detectorToSend);
            }
        }
    }
})();