(function () {
    'use strict';

    angular
        .module('ivigilate.sightings.controllers')
        .controller('SightingsController', SightingsController);

    SightingsController.$inject = ['$location', '$scope', '$filter', '$interval', 'Authentication',
        'Users', 'Beacons', 'Detectors', 'Sightings', 'Payments', 'dialogs', 'Notifications', 'leafletData'];

    function SightingsController($location, $scope, $filter, $interval, Authentication,
                                 Users, Beacons, Detectors, Sightings, Payments, dialogs, Notifications, leafletData) {
        var vm = this;
        vm.refresh = refresh;
        vm.addSighting = addSighting;
        vm.editSighting = editSighting;
        vm.editBeacon = editBeacon;
        vm.editDetector = editDetector;
        vm.confirmSighting = confirmSighting;
        vm.openDatePicker = openDatePicker;
        vm.viewGps = viewGps;
        vm.zoomToFit = zoomToFit;

        vm.sightings = undefined;
        vm.formattedSightings = undefined;

        vm.filterStartDate = vm.filterDateMax = $filter('date')(new Date(), 'yyyy-MM-dd');
        vm.filterDateIsOpen = false;

        vm.filterEndDate = vm.filterDateMax = $filter('date')(new Date(), 'yyyy-MM-dd');
        vm.filterEndDateIsOpen = false;

        vm.beaconsOrDetectors = [];
        vm.filterBeaconOrDetector = undefined;

        vm.sightingType = [{'type': 'Beacon', 'description': 'Show only Beacon Sightings'},
            {'type': 'GPS', 'description': 'Show only GPS Sightings'}];
        vm.filterSightingType = undefined;
        vm.filteredSightings = undefined;
        vm.filterChanged = false;

        vm.datepickerOptions = {
            showWeeks: false,
            sideBySide: true,
            startingDay: 1
        };
        vm.mapView = false;

        vm.map = {
            id: 'map',
            defaults: {
                tilelayer: 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                scrollWheelZoom: false
            },
            maxbounds: {'northEast': {'lat': -60, 'lng': -120}, 'southWest': {'lat': 60, 'lng': 120}},
            markers: {},
            paths: {},
            legend: {
                position: 'bottomleft'
            }
        };

        vm.colors = ['#00c6d2', '#839d57', '#f04d4c', '#65666a', '#dddddd'];
        vm.current_marker = undefined;
        vm.mapBounds = undefined;

        vm.resetValue = function ($event) {
            vm.filterBeaconOrDetector = null;
            $event.stopPropagation();
        };

        vm.resetType = function ($event) {
            vm.filterSightingType = null;
            $event.stopPropagation();
        };

        vm.setMapView = function (mapView) {
            vm.mapView = mapView;
            resizeMap();
            zoomToFit();
        };

        activate();


        function activate() {
            var user = Authentication.getAuthenticatedUser();
            if (user) {
                Payments.checkLicense(user).then(function () {
                    initAndRefresh();
                });
            }
            else {
                $location.url('/');
            }
        }

        function initAndRefresh() {
            Beacons.list().then(beaconsSuccessFn, errorFn);
            Detectors.list().then(detectorsSuccessFn, errorFn);

            $scope.$watch('vm.filterStartDate', function () {
                vm.filterStartDate = $filter('date')(vm.filterStartDate, 'yyyy-MM-dd');
                vm.filterChanged = true;
                refresh();
            });

            $scope.$watch('vm.filterEndDate', function () {
                vm.filterEndDate = $filter('date')(vm.filterEndDate, 'yyyy-MM-dd');
                vm.filterChanged = true;
                refresh();
            });


            $scope.$watch('vm.filterBeaconOrDetector', function () {
                vm.filterChanged = true;
                refresh();
            });

            $scope.$watch('vm.filterSightingType', function () {
                vm.filterChanged = true;
            });


            var refreshInterval = $interval(refresh, 2000);
            $scope.$on('$destroy', function () {
                $interval.cancel(refreshInterval);
            });
            function beaconsSuccessFn(data, status, headers, config) {
                var beacons = data.data;
                for (var i = 0; i < beacons.length; i++) {
                    beacons[i].kind = beacons[i].type_display + ' Beacon';
                }
                vm.beaconsOrDetectors.extend(beacons);
            }

            function detectorsSuccessFn(data, status, headers, config) {
                var detectors = data.data;
                for (var i = 0; i < detectors.length; i++) {
                    detectors[i].kind = detectors[i].type_display + ' Detector';
                }
                vm.beaconsOrDetectors.extend(detectors);
            }

            function errorFn(data, status, headers, config) {
                vm.error = 'Failed to get filter data with error: ' +
                data.status != 500 ? JSON.stringify(data.data) : data.statusText;
            }

            //set up map custom controls
            leafletData.getMap('mapLeaflet').then(function (map) {
                L.easyButton('fa-arrows', function () {
                    zoomToFit();
                }).addTo(map);

            });
        }

        function refresh() {
            if (vm.filterStartDate) {
                Sightings.list(vm.filterStartDate, vm.filterEndDate, vm.filterBeaconOrDetector, vm.filterShowAll).then(successFn, errorFn);
                Notifications.checkForNotifications();

            }

            function successFn(response, status, headers, config) {

                vm.error = null;
                vm.sightings = sortByKey(response.data.data, 'id');
                applyClientServerTimeOffset(response.data.timestamp);
                filterSightingsByType();
                if (vm.mapView) {
                    resizeMap();
                    setUpSightingsMap();


                    if (vm.filterChanged) {
                        zoomToFit();
                        vm.filterChanged = false;
                    }
                }
                setTimeout(prepareSightingsForExport, 50);
            }

            function errorFn(response, status, headers, config) {
                vm.error = response.status != 500 ? JSON.stringify(response.data) : response.statusText;
            }
        }

        function addSighting() {
            var dlg = dialogs.create('static/templates/sightings/addsighting.html', 'AddSightingController as vm', null, {'size': 'md'});
            dlg.result.then(function (newSighting) {
                refresh();
            });
        }

        function editSighting(sighting) {
            var dlg = dialogs.create('static/templates/sightings/editsighting.html', 'EditSightingController as vm', sighting, {'size': 'md'});
            dlg.result.then(function (editedSighting) {
                refresh();
            });
        }

        function editBeacon(beacon) {
            var dlg = dialogs.create('static/templates/beacons/editbeacon.html', 'EditBeaconController as vm', beacon, {'size': 'lg'});
            dlg.result.then(function (editedBeacon) {
                refresh();
            });
        }

        function editDetector(detector) {
            var dlg = dialogs.create('static/templates/detectors/editdetector.html', 'EditDetectorController as vm', detector, {'size': 'lg'});
            dlg.result.then(function (editedDetector) {
                refresh();
            });
        }

        function viewGps(sighting) {
            var dlg = dialogs.create('static/templates/sightings/viewgps.html', 'ViewGpsController as vm', sighting, {'size': 'lg'});
        }

        function confirmSighting(sighting) {
            Sightings.update(sighting).then(successFn, errorFn);

            function successFn(data, status, headers, config) {
                // Do nothing...
            }

            function errorFn(response, status, headers, config) {
                vm.error = response.status != 500 ? JSON.stringify(response.data) : response.statusText;
                sighting.confirmed = !sighting.confirmed;
            }
        }

        function applyClientServerTimeOffset(serverTimestamp) {
            var offset = new Date(serverTimestamp).getTime() - (new Date()).getTime();
            for (var i = 0; i < vm.sightings.length; i++) {
                vm.sightings[i].first_seen_at = new Date(vm.sightings[i].first_seen_at).getTime() - offset;
                vm.sightings[i].first_seen_at = new Date(vm.sightings[i].first_seen_at).toISOString();
                vm.sightings[i].last_seen_at = new Date(vm.sightings[i].last_seen_at).getTime() - offset;
                vm.sightings[i].last_seen_at = new Date(vm.sightings[i].last_seen_at).toISOString();
            }
        }

        function preventTimesInTheFutureToSightings() {
            if (vm.sightings) {
                var now = new Date();
                for (var i = 0; i < vm.sightings.length; i++) {
                    if (new Date(vm.sightings[i].last_seen_at) > now) {
                        vm.sightings[i].last_seen_at = now;
                    }
                }
            }
        }

        function openDatePicker($event, isOpen) {
            $event.preventDefault();
            $event.stopPropagation();
            vm[isOpen] = !vm[isOpen];
        }

        function sortByKey(array, key) {
            return array.sort(function (a, b) {
                var x = a[key];
                var y = b[key];

                if (typeof x == "string") {
                    x = x.toLowerCase();
                    y = y.toLowerCase();
                }

                return ((x < y) ? -1 : ((x > y) ? 1 : 0));
            });
        }

        function filterSightingsByType() {
            if (!vm.filterSightingType) {
                return;
            }
            vm.filteredSightings = [];
            for (var i = 0; i < vm.sightings.length; i++) {
                if (vm.filterSightingType.type === 'GPS' && vm.sightings[i].type === vm.filterSightingType.type ||
                    vm.filterSightingType.type === 'Beacon' && vm.sightings[i].type !== 'GPS') {
                    vm.filteredSightings.push(vm.sightings[i]);
                }
            }
            vm.sightings = vm.filteredSightings;
        }

        //formats sightings for exportation to CSV format
        function prepareSightingsForExport() {
            //todo: needs some improvement
            vm.formattedSightings = [];
            if (!vm.sightings || !vm.sightings.length > 0) {
                return;
            }
            var formattedSighting;
            var fields = ['beacon', 'detector', 'first_seen_at', 'last_seen_at', 'location',
                'beacon_battery', 'confirmed', 'detector_battery'];

            for (var i = 0; i < vm.sightings.length; i++) {
                formattedSighting = {};
                for (var prop in vm.sightings[i]) {
                    if (vm.sightings[i].hasOwnProperty(prop) && fields.includes(prop)) {
                        if (prop === 'beacon' || prop === 'detector') {
                            formattedSighting[prop + '_name'] = vm.sightings[i][prop] != null ? vm.sightings[i][prop]['name'] : 'GPS';
                            formattedSighting[prop + '_uid'] = vm.sightings[i][prop] != null ? vm.sightings[i][prop]['uid'] : 'N/A';
                            continue;
                        } else if (prop == 'location' && vm.sightings[i][prop] != null) {
                            formattedSighting['location'] = vm.sightings[i][prop]['coordinates'][0] + ', ' +
                                vm.sightings[i][prop]['coordinates'][1];
                            continue;
                        }
                        formattedSighting[prop] = vm.sightings[i][prop];
                    }
                }
                vm.formattedSightings.push(formattedSighting);
            }
        }


        function resizeMap() {
            leafletData.getMap('mapLeaflet').then(function (map) {
                map.options.minZoom = 1;
                setTimeout(function () {
                    map.invalidateSize();
                }, 500);
            });
        }

        function setUpSightingsMap() {
            if (!vm.sightings) {
                return;
            }
            vm.map.markers = {};
            vm.map.paths = {};
            vm.map.legend = vm.sightings.length === 0 ? undefined : {
                position: 'bottomleft',
                colors: [],
                labels: []
            };
            vm.current_marker = [];

            var uid;
            var device_name;
            var sighted_devices = [];
            var color_index = 0;
            var marker;
            var circle_marker;
            var marker_index = 0;
            var circle_marker_index = 0;

            for (var i = 0; i < vm.sightings.length; i++) {

                if (vm.sightings[i]['beacon'] && vm.sightings[i]['beacon']['type'] === 'M') {
                    uid = vm.sightings[i]['beacon']['uid'];
                    device_name = vm.sightings[i]['beacon']['name'];
                } else {
                    uid = vm.sightings[i]['detector']['uid'];
                    device_name = vm.sightings[i]['detector']['name'];
                }
                //set up path object and legend for each sighted device
                if (vm.sightings[i]['location'] && !sighted_devices.includes(uid)) {
                    sighted_devices.push(uid);
                    vm.map.paths[uid] = {
                        color: vm.colors[color_index],
                        weight: 2,
                        latlngs: [],
                        dashArray: '1, 5'
                    };
                    vm.map.legend.colors.push(vm.colors[color_index]);
                    vm.map.legend.labels.push(device_name);
                    color_index = color_index < vm.colors.length ? color_index + 1 : 0;
                    marker_index = 0;
                    circle_marker_index = 0;
                } else {
                    for (var det in vm.map.paths) {
                        if (vm.map.paths.hasOwnProperty(det) && det === device_name) {
                            circle_marker_index = vm.map.paths[det]['latlngs'].length;
                            marker_index = Math.floor(circle_marker_index / 5);
                        }
                    }
                }
                marker = uid + "_" + marker_index;
                circle_marker = uid + '_circleMarker_' + circle_marker_index;
                //set up circleMarker object for each sighting
                vm.map.paths[uid + '_circleMarker_' + circle_marker_index] = {
                    opacity: 1,
                    weight: 2,
                    latlngs: [vm.sightings[i]['location']['coordinates'][1], vm.sightings[i]['location']['coordinates'][0]],
                    radius: 5,
                    type: 'circleMarker'
                    //group: 'markers'
                };

                //set up full marker object to show at first and last location as well as every 5 sightings
                var current_marker = {
                    'lng': vm.sightings[i]['location']['coordinates'][0],
                    'lat': vm.sightings[i]['location']['coordinates'][1],
                    'message': vm.sightings[i]['beacon'] != null ?
                    vm.sightings[i]['detector']['type'] + " " + vm.sightings[i]['detector']['name'] + " with ID: " + vm.sightings[i]['detector']['uid'] +
                    "<br>" + vm.sightings[i]['beacon']['type'] + " " + vm.sightings[i]['beacon']['name'] + " with ID: " + vm.sightings[i]['beacon']['uid'] +
                    "<br>last seen: " + vm.sightings[i]['last_seen_at'].substring(0, 10) + " at " + vm.sightings[i]['last_seen_at'].substring(12, 16) :
                    vm.sightings[i]['detector']['type'] + " " + vm.sightings[i]['detector']['name'] + " with ID: " + vm.sightings[i]['detector']['uid'] +
                    "<br>last seen: " + vm.sightings[i]['last_seen_at'].substring(0, 10) + " at " + vm.sightings[i]['last_seen_at'].substring(12, 16),
                    'icon': {
                        'type': 'vectorMarker',
                        'icon': 'map-marker'
                    },
                    group: 'markers'
                };

                if (marker_index !== 0 && (circle_marker_index + 1 ) % 5 !== 0) {
                    marker_index--;
                }
                vm.map.markers[marker] = current_marker;

                //add sighting coordinates to corresponding device path array and update current marker
                for (var prop in vm.map.paths) {
                    if (vm.map.paths.hasOwnProperty(prop) && prop === uid) {
                        vm.map.paths[circle_marker]['color'] = vm.map.paths[uid]['color'];
                        vm.map.markers[marker]['icon']['markerColor'] = vm.map.paths[uid]['color'];
                        vm.map.paths[prop]['latlngs'].push(vm.map.paths[circle_marker]['latlngs']);
                        break;
                    }
                }
                //save sighting location to current markers for calculating map bounds
                vm.current_marker.push([vm.map.markers[marker]['lat'], vm.map.markers[marker]['lng']]);

                uid = "";
                marker_index++;
                circle_marker_index++;
            }
        }

        function zoomToFit() {

            if (!vm.sightings || !vm.current_marker) {
                return;
            }
            if (vm.current_marker.length === 0) {
                vm.current_marker.push([vm.map.maxbounds.northEast.lat, vm.map.maxbounds.northEast.lng],
                    [vm.map.maxbounds.southWest.lat, vm.map.maxbounds.southWest.lng]);
            }
            vm.mapBounds = new L.latLngBounds(vm.current_marker);
            leafletData.getMap('mapLeaflet').then(function (map) {
                map.fitBounds(vm.mapBounds, {padding: [30, 30]});
            });
        }


        Array.prototype.extend = function (other_array) {
            /* should include a test to check whether other_array really is an array... */
            other_array.forEach(function (v) {
                this.push(v)
            }, this);
        }
    }
})();