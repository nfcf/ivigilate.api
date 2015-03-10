(function () {
    'use strict';

    angular
        .module('ivigilate.sightings.services')
        .factory('Sightings', Sightings);

    Sightings.$inject = ['$http'];

    function Sightings($http) {

        var Sightings = {
            destroy: destroy,
            get: get,
            list: list,
            add: add,
            update: update
        };
        return Sightings;

        /////////////////////

        function destroy(sighting) {
            return $http.delete('/api/v1/sightings/' + sighting.id + '/');
        }

        function get(id) {
            return $http.get('/api/v1/sightings/' + id + '/');
        }

        function list(toDate) {
            return $http.get('/api/v1/sightings/', {params: {toDate: toDate}});
        }

        function add(sighting) {
            return $http.post('/api/v1/sightings/', sighting);
        }

        function update(sighting) {
            return $http.put('/api/v1/sightings/' + sighting.id + '/', sighting);
        }
    }
})();