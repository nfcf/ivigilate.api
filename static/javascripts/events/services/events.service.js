(function () {
    'use strict';

    angular
        .module('ivigilate.events.services')
        .factory('Events', Events);

    Events.$inject = ['$http'];

    function Events($http) {

        var Events = {
            destroy: destroy,
            get: get,
            list: list,
            add: add,
            update: update
        };
        return Events;

        /////////////////////

        function destroy(event) {
            return $http.delete('/api/v1/events/' + event.id + '/');
        }

        function get(id) {
            return $http.get('/api/v1/events/' + id + '/');
        }

        function list() {
            return $http.get('/api/v1/events/');
        }

        function add(event) {
            return $http.post('/api/v1/events/', event);
        }

        function update(event) {
            return $http.put('/api/v1/events/' + event.id + '/', event);
        }
    }
})();