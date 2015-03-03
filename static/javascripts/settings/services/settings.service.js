(function () {
  'use strict';

  angular
    .module('ivigilate.settings.services')
    .factory('Settings', Settings);

  Settings.$inject = ['$http'];

  function Settings($http) {

    var Settings = {
      destroy: destroy,
      get: get,
      update: update
    };
    return Settings;

    /////////////////////

    function destroy(user) {
      return $http.delete('/api/v1/users/' + user.id + '/');
    }

    function get(id) {
      return $http.get('/api/v1/users/' + id + '/');
    }

    function update(user) {
      return $http.put('/api/v1/users/' + user.id + '/', user);
    }
  }
})();