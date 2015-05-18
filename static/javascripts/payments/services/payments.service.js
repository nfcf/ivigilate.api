(function () {
    'use strict';

    angular
        .module('ivigilate.payments.services')
        .factory('Payments', Payments);

    Payments.$inject = ['$http'];

    function Payments($http) {

        var Payments = {
            charge: charge
        };
        return Payments;

        /////////////////////

        function charge(tokenID, receiptEmail) {
            return $http.post('/api/v1/makepayment/', {'token_id': tokenID, 'receipt_email': receiptEmail});
        }
    }
})();