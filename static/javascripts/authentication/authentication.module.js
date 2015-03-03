(function () {
  'use strict';

  angular
    .module('ivigilate.authentication', [
      'ivigilate.authentication.controllers',
      'ivigilate.authentication.services'
    ]);

  angular
    .module('ivigilate.authentication.controllers', []);

  angular
    .module('ivigilate.authentication.services', ['ngCookies']);
})();