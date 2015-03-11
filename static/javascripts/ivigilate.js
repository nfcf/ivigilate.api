(function () {
    'use strict';

    angular
        .module('ivigilate', [
            'uiGmapgoogle-maps',
            'uiGmapgoogle-maps.providers',
            'smart-table',
            'ngPasswordStrength',
            'ui.bootstrap',
            'dialogs.main',
            'relativeDate',
            'pascalprecht.translate',
            'ngSanitize',
            'ui.select',
            'ivigilate.config',
            'ivigilate.filters',
            'ivigilate.routes',
            'ivigilate.authentication',
            'ivigilate.layout',
            'ivigilate.settings',
            'ivigilate.places',
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
        .run(run);

    run.$inject = ['$http'];

    /**
     * @name run
     * @desc Update xsrf $http headers to align with Django's defaults
     */
    function run($http) {
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
        $http.defaults.xsrfCookieName = 'csrftoken';
    }
})();