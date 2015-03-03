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
      controller: 'SettingsController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/authentication/settings.html'
    }).when('/places', {
      controller: 'PlacesController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/places/places.html'
    }).when('/places/:place_id', {
      controller: 'PlaceController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/places/place.html'
    }).otherwise('/');
  }
})();