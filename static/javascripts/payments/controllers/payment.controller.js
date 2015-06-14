(function () {
    'use strict';

    angular
        .module('ivigilate.payments.controllers')
        .controller('PaymentController', PaymentController);

    PaymentController.$inject = ['$location', '$scope', '$timeout', '$modalInstance', 'data',
        'Authentication', 'Payments', 'stripe'];

    function PaymentController($location, $scope, $timeout, $modalInstance, data,
                               Authentication, Payments, stripe) {
        var vm = this;
        vm.skip = skip;
        vm.charge = charge;

        vm.error = undefined;
        vm.title = undefined;
        vm.header = undefined;
        vm.license = undefined;
        vm.canSkip = false;
        vm.card = {};

        activate();

        function activate() {
            var user = Authentication.getAuthenticatedUser();
            if (user) {
                if (user.license_about_to_expire != null) {
                    vm.license = user.license_about_to_expire;
                    var metadata = JSON.parse(vm.license.metadata);
                    vm.title = 'Your license is about to expire...';
                    vm.header = 'Please renew you subscription before ' +
                    date2str(new Date(vm.license.valid_until), 'yyyy-MM-dd hh:mm');
                    vm.license.max_beacons = metadata.max_beacons;
                    vm.license.max_users = metadata.max_users;
                    vm.canSkip = true;
                } else {
                    vm.license = user.license_due_for_payment;
                    var metadata = JSON.parse(vm.license.metadata);
                    vm.title = 'Your license is due for payment...';
                    vm.header = 'Please renew you subscription.';
                    vm.license.max_beacons = metadata.max_beacons;
                    vm.license.max_users = metadata.max_users;
                }
            }
            else {
                $location.url('/');
            }
        }

        function charge(card) {
            $scope.$broadcast('show-errors-check-validity');

            if (vm.paymentForm.$valid) {
                vm.error = '';
                return stripe.card.createToken(card)
                    .then(function (token) {
                        return Payments.charge(token.id, vm.card.receipt_email);
                    })
                    .then(function (data) {
                        var license = data.data;
                        $modalInstance.close(license);
                    })
                    .catch(function (err) {
                        if (err.type && /^Stripe/.test(err.type)) {
                            vm.error = 'Stripe error: ' + err.message;
                        }
                        else {
                            vm.error = err.status != 500 ? JSON.stringify(err.data) : err.statusText;
                        }
                    });
            } else {
                vm.error = 'There are invalid fields in the form.';
            }
        }

        function skip() {
            $modalInstance.dismiss('Skip');
        }

        function date2str(x, y) {
            var z = {
                M: x.getMonth() + 1,
                d: x.getDate(),
                h: x.getHours(),
                m: x.getMinutes(),
                s: x.getSeconds()
            };
            y = y.replace(/(M+|d+|h+|m+|s+)/g, function (v) {
                return ((v.length > 1 ? "0" : "") + eval('z.' + v.slice(-1))).slice(-2)
            });

            return y.replace(/(y+)/g, function (v) {
                return x.getFullYear().toString().slice(-v.length)
            });
        }
    }
})
();