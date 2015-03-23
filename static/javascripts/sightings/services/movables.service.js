(function () {
    'use strict';

    angular
        .module('ivigilate.movables.services')
        .factory('Movables', Movables);

    Movables.$inject = ['$http', '$upload'];

    function Movables($http, $upload) {

        var Movables = {
            destroy: destroy,
            get: get,
            list: list,
            update: update
        };
        return Movables;

        /////////////////////

        function destroy(movable) {
            return $http.delete('/api/v1/movables/' + movable.id + '/');
        }

        function get(id) {
            return $http.get('/api/v1/movables/' + id + '/');
        }

        function list() {
            return $http.get('/api/v1/movables/');
        }

        function update(movable) {
            return $http.put('/api/v1/movables/' + movable.id + '/', movable);
        }

        function update(movable, image) {
            return $upload.upload({
                url: '/api/v1/movables/' + movable.id + '/',
                method: 'PUT',
                fields: movable,
                file: image,
                fileFormDataName: 'photo'
            });
        }
    }
})();