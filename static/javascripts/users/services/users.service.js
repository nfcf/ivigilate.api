(function () {
    'use strict';

    angular
        .module('ivigilate.users.services')
        .factory('Users', Users);

    Users.$inject = ['$http', '$upload'];

    function Users($http, $upload) {

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

        function update(user, image) {
            var userToSend = JSON.parse(JSON.stringify(user));
            userToSend.photo = undefined;
            if (!!image) {
                return $upload.upload({
                    url: '/api/v1/users/' + userToSend.id + '/',
                    method: 'PUT',
                    fields: userToSend,
                    file: image,
                    fileFormDataName: 'photo'
                });
            } else {
                return $http.put('/api/v1/users/' + userToSend.id + '/', userToSend);
            }
        }
    }
})();