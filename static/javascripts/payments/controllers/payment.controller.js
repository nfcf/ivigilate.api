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
                    date2str(convertUTCDateToLocalDate(new Date(vm.license.valid_until)), 'yyyy-MM-dd hh:mm');
                    vm.license.duration = metadata.duration_in_months;
                    vm.license.max_movables = metadata.max_movables;
                    vm.license.max_users = metadata.max_users;
                    vm.canSkip = true;
                } else {
                    vm.license = user.license_due_for_payment;
                    var metadata = JSON.parse(vm.license.metadata);
                    vm.title = 'Your license has expired...';
                    vm.header = 'Please renew you subscription.';
                    vm.license.duration = metadata.description;
                    vm.license.max_movables = metadata.max_movables;
                    vm.license.max_users = metadata.max_users;
                }
            }
            else {
                $location.url('/');
            }
        }

        function charge(card) {
            return stripe.card.createToken(card)
                .then(function (token) {
                    return Payments.charge(token.id, vm.card.receipt_email);
                })
                .then(function (data) {
                    var license = data.data;
                    console.log('successfully submitted payment for ', license.currency, license.amount);
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
        }

        function skip() {
            $modalInstance.dismiss('Skip');
        }

        function convertUTCDateToLocalDate(date) {
            var newDate = new Date(date.getTime() + date.getTimezoneOffset() * 60 * 1000);

            var offset = date.getTimezoneOffset() / 60;
            var hours = date.getHours();

            newDate.setHours(hours - offset);

            return newDate;
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