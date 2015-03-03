(function () {
    'use strict';

    angular
        .module('ivigilate.places.services')
        .factory('Places', Places);

    Places.$inject = ['$http'];

    function Places($http) {

        var Places = {
            destroy: destroy,
            get: get,
            list: list,
            update: update
        };
        return Places;

        /////////////////////

        function destroy(place) {
            return $http.delete('/api/v1/places/' + place.id + '/');
        }

        function get(id) {
            return $http.get('/api/v1/places/' + id + '/');
        }

        function list() {
            return $http.get('/api/v1/places/');
        }

        function update(place) {
            return $http.put('/api/v1/places/' + place.id + '/', place).then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                //Authentication.login(email, password);
            }

            function errorFn(data, status, headers, config) {
                console.error(data.data.status + ": " + data.data.message);
                alert(data.data.status + ": " + data.data.message);
            }
        }
    }
})();