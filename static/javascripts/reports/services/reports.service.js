(function () {
    'use strict';

    angular
        .module('ivigilate.reports.services')
        .factory('Reports', Reports);

    Reports.$inject = ['$http'];

    function Reports($http) {

        var Reports = {
            get: get
        };
        return Reports;

        /////////////////////

        function get(filter) {
            var url = '/report/?report_type=' + filter.report_type +
                      '&from_date=' + filter.from_date.toISOString().substring(0, 18) +
                      '&to_date=' + filter.to_date.toISOString().substring(0, 18);
            window.open(url, '_blank'); // in new tab
        }

    }
})();