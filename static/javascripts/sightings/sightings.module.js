(function () {
    'use strict';

    angular
        .module('ivigilate.sightings', [
            'ivigilate.sightings.controllers',
            'ivigilate.sightings.services',
            'ivigilate.beacons.services'
        ]);


    angular
        .module('ivigilate.sightings.controllers', []);

    angular
        .module('ivigilate.sightings.services', []);

    angular
        .module('ivigilate.beacons.services', []);

})();