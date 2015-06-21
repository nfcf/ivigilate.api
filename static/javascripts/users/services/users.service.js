(function () {
    'use strict';

    angular
        .module('ivigilate.users.services')
        .factory('Users', Users);

    Users.$inject = ['$http'];

    function Users($http) {

        var Users = {
            destroy: destroy,
            get: get,
            list: list,
            update: update
        };
        return Users;

        /////////////////////

        function destroy(user) {
            return $http.delete('/api/v1/users/' + user.id + '/');
        }

        function get(id) {
            return $http.get('/api/v1/users/' + id + '/');
        }

        function list() {
            return $http.get('/api/v1/users/');
        }

        function update(user) {
            return $http.put('/api/v1/users/' + user.id + '/', user);
        }
    }
})();