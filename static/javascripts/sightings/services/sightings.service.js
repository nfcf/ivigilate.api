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

        function list(filterDate, filterEndDate, filterBeaconOrDetector, filterShowAll) {
            var filterTimezoneOffset = new Date().getTimezoneOffset();
            var filterBeaconsIds = [];
            var filterDetectorsIds = [];
            
            var request;

            if (filterBeaconOrDetector == null || filterBeaconOrDetector.kind.indexOf('Beacon') >= 0) {
                var params = !filterBeaconOrDetector ? {
                        params: {
                            filterTimezoneOffset: filterTimezoneOffset,
                            filterDate: filterDate,
                            filterEndDate: filterEndDate,
                            filterBeacons: undefined,
                            filterDetectors: undefined,
                            filterShowAll: filterShowAll
                        }
                    } : {
                        params: {
                            beaconId: filterBeaconOrDetector.uid,
                            filterDate: filterDate,
                            filterEndDate: filterEndDate
                        }
                    }


                request = $http.get('/api/v1/beaconhistory/', params);

            } else if (filterBeaconOrDetector.kind.indexOf('Detector') >= 0) {
                request = $http.get('/api/v1/detectorhistory/',
                    {
                        params: {
                            detectorId: filterBeaconOrDetector.uid,
                            filterDate: filterDate,
                            filterEndDate: filterEndDate
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