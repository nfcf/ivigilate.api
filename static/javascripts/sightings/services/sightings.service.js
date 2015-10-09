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

        function list(filterDate, filterFixedBeaconsAndDetectors, filterShowAll) {
            var filterTimezoneOffset = new Date().getTimezoneOffset();
            var filterBeaconsIds = [];
            var filterDetectorsIds = [];
            if (filterFixedBeaconsAndDetectors != null && filterFixedBeaconsAndDetectors.length > 0) {
                filterFixedBeaconsAndDetectors.forEach(function(fixedBeaconOrDetector) {
                    if (fixedBeaconOrDetector.kind.indexOf('Beacon') >= 0) filterBeaconsIds.push(fixedBeaconOrDetector.id);
                    else if (fixedBeaconOrDetector.kind.indexOf('Detector') >= 0) filterDetectorsIds.push(fixedBeaconOrDetector.id);
                })
            }
            return $http.get('/api/v1/sightings/',
                {
                    params: {
                        filterTimezoneOffset: filterTimezoneOffset,
                        filterDate: filterDate,
                        filterBeacons: filterBeaconsIds.length > 0 ? filterBeaconsIds : undefined,
                        filterDetectors: filterDetectorsIds.length > 0 ? filterDetectorsIds : undefined,
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
            return $http.put('/api/v1/sightings/' + sightingToSend.id + '/', sightingToSend);
        }
    }
})();