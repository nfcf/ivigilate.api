(function () {
    'use strict';

    angular
        .module('ivigilate.limits.controllers')
        .controller('LimitsController', LimitsController);

    LimitsController.$inject = ['$location', '$scope', 'Authentication', 'Limits', 'Payments', 'dialogs'];

    function LimitsController($location, $scope, Authentication, Limits, Payments, dialogs) {
        var vm = this;
        vm.refresh = refresh;
        vm.addLimit = addLimit;
        vm.editLimit = editLimit;
        vm.updateLimitState = updateLimitState;

        vm.limits = undefined;

        activate();

        function activate() {
            var user = Authentication.getAuthenticatedUser();
            if (user) {
                Payments.checkLicense(user).then(function () { refresh(); });
            }
            else {
                $location.url('/');
            }
        }

        function refresh() {
            Limits.list().then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                vm.limits = data.data;
                for (var i = 0; i < vm.limits.length; i++) {
                    var limit = vm.limits[i];
                    limit.events_display_string = !!limit.events && limit.events.length == 1 ?
                                                         limit.events[0].name :
                                                         !!limit.events && limit.events.length > 1 ?
                                                         limit.events.length + ' event(s)' : '(Any)';
                    limit.beacons_display_string = !!limit.beacons && limit.beacons.length == 1 ?
                                                         limit.beacons[0].name :
                                                         !!limit.beacons && limit.beacons.length > 1 ?
                                                         limit.beacons.length + ' beacon(s)' : '(Any)';
                    limit.start_date = date2str(new Date(limit.start_date), 'yyyy-MM-dd');

                    if (!!limit.metadata) {
                        var metadata = JSON.parse(limit.metadata);

                        limit.metadata_object = {};
                        limit.metadata_object.occurrence_date_limit = !!metadata.occurrence_date_limit ?
                                                                    date2str(new Date(metadata.occurrence_date_limit), 'yyyy-MM-dd') : 'N/A';
                        limit.metadata_object.occurrence_count_limit =  !!metadata.occurrence_count_limit && metadata.occurrence_count_limit >= 0 ?
                                                                    metadata.occurrence_count_limit : 'N/A';
                        limit.metadata_object.consider_each_beacon_separately = !!metadata.consider_each_beacon_separately;
                    }
                }
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
            }
        }

        function addLimit() {
            var dlg = dialogs.create('static/templates/limits/addeditlimit.html', 'AddEditLimitController as vm', null, {'size': 'lg'});
            dlg.result.then(function (newLimit) {
                refresh();
            });
        }

        function editLimit(limit) {
            var dlg = dialogs.create('static/templates/limits/addeditlimit.html', 'AddEditLimitController as vm', limit, {'size': 'lg'});
            dlg.result.then(function (editedLimit) {
                if (editedLimit) {
                    refresh();
                    //for (var k in editedLimit) { //Copy the object attributes to the currently displayed on the table
                    //    limit[k] = editedLimit[k];
                    //}
                } else {
                    var index = vm.limits.indexOf(limit);
                    if (index >= 0) vm.limits.splice(index, 1);
                }
            });
        }

        function updateLimitState(limit) {
            var limitToSend = JSON.parse(JSON.stringify(limit));
            limitToSend.events = null;
            limitToSend.beacons = null;
            Limits.update(limitToSend).then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                // Do nothing...
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
                limit.is_active = !limit.is_active;
            }
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
})();