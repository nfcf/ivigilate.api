(function () {
    'use strict';

    angular
        .module('ivigilate.places.services')
        .factory('Places', Places);

    Places.$inject = ['$http'];

    function Places($http) {

        var Places = {
            destroy: destroy,
            get: get,
            list: list,
            update: update
        };
        return Places;

        /////////////////////

        function destroy(place) {
            return $http.delete('/api/v1/places/' + place.id + '/');
        }

        function get(id) {
            return $http.get('/api/v1/places/' + id + '/');
        }

        function list() {
            return $http.get('/api/v1/places/');
        }

        function update(place) {
            return $http.put('/api/v1/places/' + place.id + '/', place);
        }
    }
})();