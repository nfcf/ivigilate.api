(function () {
    'use strict';

    angular
        .module('ivigilate.movables.services')
        .factory('Movables', Movables);

    Movables.$inject = ['$http'];

    function Movables($http) {

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
    }
})();