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

        function list(filterStartDate, filterEndDate, filterBeaconOrDetector, filterShowAll) {
            var filterTimezoneOffset = new Date().getTimezoneOffset();
            filterStartDate = filterStartDate + ":00";
            filterEndDate = filterEndDate + ":59";


            return $http.get('/api/v1/sightings/',
                {
                    params: {
                        timezoneOffset: filterTimezoneOffset,
                        beaconId: filterBeaconOrDetector && filterBeaconOrDetector.kind.indexOf('Beacon') >= 0 ? filterBeaconOrDetector.uid : undefined,
                        detectorId: filterBeaconOrDetector && filterBeaconOrDetector.kind.indexOf('Detector') >= 0 ? filterBeaconOrDetector.uid : undefined,
                        startDate: filterStartDate,
                        endDate: filterEndDate
                    }
                });
            
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