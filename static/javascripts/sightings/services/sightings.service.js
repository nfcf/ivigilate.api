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

        function list(filterDate, filterPlaces, filterShowAll) {
            var filterPlacesIds = undefined;
            if (filterPlaces != null && filterPlaces.length > 0) {
                filterPlacesIds = [];
                filterPlaces.forEach(function(place) {
                    filterPlacesIds.push(place.id);
                })
            }
            return $http.get('/api/v1/sightings/',
                {
                    params: {
                        filterDate: filterDate,
                        filterPlaces: filterPlacesIds !== undefined ? filterPlacesIds : undefined,
                        filterShowAll: filterShowAll}
                }
            );
        }

        function add(sighting) {
            return $http.post('/api/v1/sightings/', sighting);
        }

        function update(sighting) {
            var sightingToSend = JSON.parse(JSON.stringify(sighting));
            sightingToSend.beacon = sighting.beacon.id;  // Required for the REST serializer
            sightingToSend.place = !!sighting.place ? sighting.place.id : null;  // Required for the REST serializer
            sightingToSend.user = !!sighting.user ? sighting.user.id : null;  // Required for the REST serializer
            return $http.put('/api/v1/sightings/' + sightingToSend.id + '/', sightingToSend);
        }
    }
})();