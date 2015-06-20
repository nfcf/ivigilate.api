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

        function list(filterDate, filterPlacesAndUsers, filterShowAll) {
            var filterBeaconsIds = [];
            var filterDetectorsIds = [];
            var filterUsersIds = [];
            if (filterPlacesAndUsers != null && filterPlacesAndUsers.length > 0) {
                filterPlacesAndUsers.forEach(function(placeOrUser) {
                    if (placeOrUser.kind == 'Fixed Beacon') filterBeaconsIds.push(placeOrUser.id);
                    else if (placeOrUser.kind == 'Fixed Detector') filterDetectorsIds.push(placeOrUser.id);
                    else if (placeOrUser.kind == 'User') filterUsersIds.push(placeOrUser.id);
                })
            }
            return $http.get('/api/v1/sightings/',
                {
                    params: {
                        filterDate: filterDate,
                        filterBeacons: filterBeaconsIds.length > 0 ? filterBeaconsIds : undefined,
                        filterDetectors: filterDetectorsIds.length > 0 ? filterDetectorsIds : undefined,
                        filterUsers: filterUsersIds.length > 0 ? filterUsersIds : undefined,
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
            sightingToSend.detector = !!sighting.detector ? sighting.detector.id : null;  // Required for the REST serializer
            sightingToSend.user = !!sighting.user ? sighting.user.id : null;  // Required for the REST serializer
            return $http.put('/api/v1/sightings/' + sightingToSend.id + '/', sightingToSend);
        }
    }
})();