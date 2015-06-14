(function () {
    'use strict';

    angular
        .module('ivigilate.payments.services')
        .factory('Payments', Payments);

    Payments.$inject = ['$http', 'Authentication', 'dialogs'];

    function Payments($http, Authentication, dialogs) {

        var Payments = {
            checkLicense: checkLicense,
            charge: charge
        };
        return Payments;

        /////////////////////

        function checkLicense(user) {
            return new Promise(function (resolve, reject) {
                if (user.is_account_admin) {
                    if (user.license_due_for_payment) {
                        var dlg = dialogs.create('static/templates/payments/payment.html', 'PaymentController as vm', user, {'size': 'md'});
                        dlg.result.then(function (license) {
                            user.license_about_to_expire = null;
                            user.license_due_for_payment = null;
                            Authentication.setAuthenticatedUser(user);
                            resolve();
                        }, function (skipped) {
                            resolve();
                        });
                    } else {
                        resolve();
                    }
                } else {
                    resolve();
                }
            });
        }

        function charge(tokenID, receiptEmail) {
            return $http.post('/api/v1/makepayment/', {'token_id': tokenID, 'receipt_email': receiptEmail});
        }
    }
})();