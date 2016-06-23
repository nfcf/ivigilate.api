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
            filterStartDate = filterStartDate + "T00:00:00";
            filterEndDate = filterEndDate + "T23:59:59";

            var request;

            if (filterBeaconOrDetector == null || filterBeaconOrDetector.kind.indexOf('Beacon') >= 0) {
                request = $http.get('/api/v1/beaconhistory/',
                    {
                        params: {
                            timezoneOffset: filterTimezoneOffset,
                            beaconId: !filterBeaconOrDetector ? undefined : filterBeaconOrDetector.uid,
                            startDate: filterStartDate,
                            endDate: filterEndDate
                        }
                    });

            } else if (filterBeaconOrDetector.kind.indexOf('Detector') >= 0) {
                request = $http.get('/api/v1/detectorhistory/',
                    {
                        params: {
                            timezoneOffset: filterTimezoneOffset,
                            detectorId: filterBeaconOrDetector.uid,
                            startDate: filterStartDate,
                            endDate: filterEndDate
                        }
                    }
                )
            }

            return request;
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