(function () {
    'use strict';

    angular
        .module('ivigilate.payments.controllers')
        .controller('PaymentController', PaymentController);

    PaymentController.$inject = ['$location', '$scope', '$timeout', '$modalInstance', 'data', 'Authentication', 'stripe'];

    function PaymentController($location, $scope, $timeout, $modalInstance, data, Authentication, stripe) {
        var vm = this;
        vm.skip = skip;
        vm.charge = charge;

        vm.error = undefined;
        vm.payment = {};

        activate();

        function activate() {
            var user = Authentication.getAuthenticatedUser();
            if (user) {

            }
            else {
                $location.url('/');
            }
        }

        function charge() {
            return stripe.card.createToken(vm.payment.card)
                .then(function (token) {
                    console.log('token created for card ending in ', token.card.last4);
                    var payment = angular.copy(vm.payment);
                    payment.card = void 0;
                    payment.token = token.id;
                    //return $http.post('https://yourserver.com/payments', payment);
                })
                .then(function (payment) {
                    console.log('successfully submitted payment for $ $', payment.currency, payment.amount);
                })
                .catch(function (err) {
                    if (err.type && /^Stripe/.test(err.type)) {
                        console.log('Stripe error: ', err.message);
                    }
                    else {
                        console.log('Other error occurred, possibly with your API', err.message);
                    }
                });
        }

        function skip() {
            $modalInstance.dismiss('Skip');
        }
    }
})
();