(function () {
    'use strict';

    angular
        .module('ivigilate', [
            'uiGmapgoogle-maps',
            'smart-table',
            'ivigilate.config',
            'ivigilate.routes',
            'ivigilate.authentication',
            'ivigilate.layout',
            'ivigilate.settings',
            'ivigilate.places'
        ]);

    angular
        .module('ivigilate.config', []);

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