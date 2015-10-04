(function () {
    'use strict';

    angular
        .module('ivigilate.limits.services')
        .factory('Limits', Limits);

    Limits.$inject = ['$http'];

    function Limits($http) {

        var Limits = {
            destroy: destroy,
            get: get,
            list: list,
            add: add,
            update: update
        };
        return Limits;

        /////////////////////

        function destroy(limit) {
            return $http.delete('/api/v1/limits/' + limit.id + '/');
        }

        function get(id) {
            return $http.get('/api/v1/limits/' + id + '/');
        }

        function list() {
            return $http.get('/api/v1/limits/');
        }

        function add(limit) {
            return $http.post('/api/v1/limits/', limit);
        }

        function update(limit) {
            return $http.put('/api/v1/limits/' + limit.id + '/', limit);
        }
    }
})();