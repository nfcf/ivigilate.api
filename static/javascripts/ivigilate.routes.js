(function () {
    'use strict';

    angular
        .module('ivigilate.routes')
        .config(config);

    config.$inject = ['$routeProvider'];

    function config($routeProvider) {
        $routeProvider.when('/register', {
            controller: 'RegisterController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/authentication/register.html'
        }).when('/login', {
            controller: 'LoginController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/authentication/login.html'
        }).when('/settings', {
            controller: 'UsersController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/settings/settings.html'
        }).when('/reports', {
            controller: 'ReportsController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/reports/reports.html'
        }).when('/detectors', {
            controller: 'DetectorsController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/detectors/detectors.html'
        }).when('/beacons', {
            controller: 'BeaconsController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/beacons/beacons.html'
        }).when('/events', {
            controller: 'EventsController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/events/events.html'
        }).when('/sightings', {
            controller: 'SightingsController',
            controllerAs: 'vm',
            templateUrl: '/static/templates/sightings/sightings.html'
        }).otherwise({
            redirectTo: '/login'
        });
    }
})();