(function () {
    'use strict';

    angular
        .module('ivigilate', [
            'uiGmapgoogle-maps',
            'uiGmapgoogle-maps.providers',
            'smart-table',
            'ngPasswordStrength',
            'ui.bootstrap',
            'ui.bootstrap.datetimepicker',
            'ui.bootstrap.showErrors',
            'toggle-switch',
            'angularFileUpload',
            'dialogs.main',
            'relativeDate',
            'pascalprecht.translate',
            'ngAnimate',
            'ngSanitize',
            'ui.select',
            'ngTouch',
            'ngAudio',
            'toastr',
            'angular-carousel',
            'angular-stripe',
            'credit-cards',
            'ivigilate.config',
            'ivigilate.filters',
            'ivigilate.routes',
            'ivigilate.authentication',
            'ivigilate.notifications',
            'ivigilate.payments',
            'ivigilate.layout',
            'ivigilate.users',
            'ivigilate.reports',
            'ivigilate.detectors',
            'ivigilate.beacons',
            'ivigilate.events',
            'ivigilate.limits',
            'ivigilate.sightings'
        ]);

    angular
        .module('ivigilate.config', []);

    angular
        .module('ivigilate.filters', []);

    angular
        .module('ivigilate.routes', ['ngRoute']);

    angular
        .module('ivigilate')

})();