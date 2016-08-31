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

        vm.startDate = new Date();
        vm.startDate.setHours(0, 0, 0, 0);
        vm.filterStartDate = vm.filterDateMax = $filter('date')(vm.startDate, 'yyyy-MM-ddTHH:mm');
        vm.filterDateIsOpen = false;

        vm.endDate = new Date();
        vm.endDate.setHours(23, 59, 59, 59);
        vm.filterEndDate = vm.filterDateMax = $filter('date')(vm.endDate, 'yyyy-MM-ddTHH:mm');
        vm.filterEndDateIsOpen = false;

        vm.beaconsOrDetectors = [];
        vm.filterBeaconOrDetector = undefined;
        vm.timeZoneOffset = new Date().getTimezoneOffset();

        vm.sightingType = [{'type': 'Beacon', 'description': 'Show only Beacon Sightings'},
            {'type': 'GPS', 'description': 'Show only GPS Sightings'}];
        vm.filterSightingType = undefined;
        vm.filteredSightings = undefined;
        vm.filterChanged = false;

        vm.dateTimePickerButtonBar = {
            show: true,
            now: {
                show: true,
                text: 'Now'
            },
            today: {
                show: true,
                text: 'Today'
            },
            clear: {
                show: false,
                text: 'Clear'
            },
            date: {
                show: true,
                text: 'Date'
            },
            time: {
                show: true,
                text: 'Time'
            },
            close: {
                show: true,
                text: 'Close'
            }
        };

        vm.startDatepickerOptions = {
            maxDate: vm.endDate,
            showWeeks: false,
            sideBySide: true,
            startingDay: 1
        };

        vm.endDatepickerOptions = {
            minDate: vm.startDate,
            maxDate: new Date(),
            showWeeks: false,
            sideBySide: true,
            startingDay: 1
        };

        vm.timepickerOptions = {
            hourStep: 1,
            minuteStep: 1,
            showMeridian: false
        };


        vm.mapView = false;

        vm.map = {
            id: 'map',
            defaults: {
                scrollWheelZoom: false
            },
            maxbounds: {'northEast': {'lat': -90, 'lng': -120}, 'southWest': {'lat': 90, 'lng': 120}},
            markers: {},
            paths: {},
            legend: {
                position: 'bottomleft'
            },
            layers: {
                baselayers: {
                    xyz: {
                        name: 'OpenStreetMap (XYZ)',
                        url: 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                        type: 'xyz'
                    }
                },
                overlays: {
                    sightings: {
                        name: "sightings",
                        type: "markercluster",
                        visible: true
                    }
                }
            }
        };


        vm.colors = ['#00c6d2', '#839d57', '#f04d4c', '#65666a', '#dddddd'];
        vm.current_markers = undefined;
        vm.mapBounds = undefined;
        vm.current_markers = undefined;
        vm.pathsOn = false;

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

            $scope.$watch('vm.startDate', function () {
                vm.filterStartDate = $filter('date')(vm.startDate, 'yyyy-MM-ddTHH:mm');
                vm.endDatepickerOptions.minDate = vm.startDate;
                vm.filterChanged = true;
                refresh();
            });

            $scope.$watch('vm.endDate', function () {
                vm.filterEndDate = $filter('date')(vm.endDate, 'yyyy-MM-ddTHH:mm');
                vm.startDatepickerOptions.maxDate = vm.endDate;
                vm.filterChanged = true;
                refresh();
            });


            $scope.$watch('vm.filterBeaconOrDetector', function () {
                vm.filterChanged = true;
                refresh();
            });


            $scope.$watch('vm.pathsOn', function () {
                vm.filterChanged = true;
                refresh();
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
                L.easyButton('fa-road', function () {
                    togglePathsOn();
                    showPaths();
                }).addTo(map);


            });
        }

        function refresh() {
            if (vm.filterStartDate && vm.filterEndDate) {
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
                        setTimeout(zoomToFit, 500);
                        showPaths();
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
            angular.forEach(vm.sightings, function (sighting) {
                if (vm.filterSightingType.type === 'GPS' && sighting.type === vm.filterSightingType.type ||
                    vm.filterSightingType.type === 'Beacon' && sighting.type !== 'GPS') {
                    vm.filteredSightings.push(sighting);
                }
            });
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

            angular.forEach(vm.sightings, function (sighting) {
                formattedSighting = {};
                angular.forEach(sighting, function (value, key) {
                    if (fields.includes(key)) {
                        if (key === 'beacon' || key === 'detector') {
                            formattedSighting[key + '_name'] = value != null ? value['name'] : 'GPS';
                            formattedSighting[key + '_uid'] = value != null ? value['uid'] : 'N/A';
                            return;
                        } else if (key == 'location' && value != null) {
                            formattedSighting['location'] = value['coordinates'][0] + ', ' +
                                value['coordinates'][1];
                            return;
                        }
                        formattedSighting[key] = value;
                    }
                });
                vm.formattedSightings.push(formattedSighting);
            });
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
            vm.current_markers = [];

            var uid;
            var device_name;
            var sighted_devices = [];
            var color_index = 0;
            var circle_marker;
            var circle_marker_index = 0;
            var color;
            var utc_date;
            var last_seen;

            angular.forEach(vm.sightings, function (sighting) {

                if (sighting['beacon'] && sighting['beacon']['type'] === 'M') {
                    uid = sighting['beacon']['uid'];
                    device_name = sighting['beacon']['name'];
                } else {
                    uid = sighting['detector']['uid'];
                    device_name = sighting['detector']['name'];
                }

                //set up path object and legend for each new sighted device
                if (sighting['location']) {
                    if (!sighted_devices.includes(uid)) {
                        sighted_devices.push(uid);
                        vm.map.paths[uid] = {
                            color: vm.colors[color_index],
                            latlngs: [],
                            dashArray: '3, 5',
                            dashOffset: 10
                        };
                        vm.map.legend.colors.push(vm.colors[color_index]);
                        vm.map.legend.labels.push(device_name);
                        color_index = color_index < vm.colors.length ? color_index + 1 : 0;
                        circle_marker_index = 0;
                    } else {
                        //if device was already sighted update current marker index according to number of previous sightings
                        angular.forEach(vm.map.paths, function (path, key) {
                            if (key === uid) {
                                circle_marker_index = path['latlngs'].length
                            }
                        });
                    }
                }

                //update timestamp to display in map
                utc_date = new Date(sighting['last_seen_at']);
                last_seen = (new Date(utc_date.getTime() + vm.timeZoneOffset * -60000)).toISOString();

                //set up circleMarker (vector path) object for each sighting
                circle_marker = uid + '_circleMarker_' + circle_marker_index;
                vm.map.paths[circle_marker] = {
                    type: 'circleMarker',
                    latlngs: [sighting['location']['coordinates'][1], sighting['location']['coordinates'][0]],
                    radius: 5,
                    message: 'last seen : ' + last_seen.substring(0, 10) + " at " + last_seen.substring(11, 16),
                    clickable: true
                };

                //set up full marker object to show at last sighting location, overwriting previous one if it exists
                vm.map.markers[uid] = {
                    'lng': sighting['location']['coordinates'][0],
                    'lat': sighting['location']['coordinates'][1],
                    'message': sighting['beacon'] != null ?
                    sighting['detector']['type'] + " " + sighting['detector']['name'] + " with ID: " + sighting['detector']['uid'] +
                    "<br>" + sighting['beacon']['type'] + " " + sighting['beacon']['name'] + " with ID: " + sighting['beacon']['uid'] +
                    "<br>last seen: " + last_seen.substring(0, 10) + " at " + last_seen.substring(11, 16) :
                    sighting['detector']['type'] + " " + sighting['detector']['name'] + " with ID: " + sighting['detector']['uid'] +
                    "<br>last seen: " + last_seen.substring(0, 10) + " at " + last_seen.substring(11, 16),
                    'icon': {
                        'type': 'vectorMarker',
                        'icon': 'male'
                    },
                    layer: 'sightings'
                };

                //update current marker and circle_marker color and add sighting coordinates to corresponding array for device path calculation
                for (var prop in vm.map.paths) {
                    if (vm.map.paths.hasOwnProperty(prop) && prop === uid) {
                        vm.map.paths[circle_marker]['color'] = vm.map.paths[uid]['color'];
                        vm.map.markers[uid]['icon']['markerColor'] = vm.map.paths[uid]['color'];
                        vm.map.paths[prop]['latlngs'].push(vm.map.paths[circle_marker]['latlngs']);
                        break;
                    }
                }

                //if showing sighting paths, push sighting location to current markers for calculating current map bounds
                if (vm.pathsOn) {
                    vm.current_markers.push(vm.map.paths[circle_marker]['latlngs']);
                }
                uid = "";
                circle_marker_index++;
            });

            //if showing current markers only , push sighting locations to current markers for calculating current map bounds
            if (!vm.pathsOn) {
                angular.forEach(vm.map.markers, function (marker, key) {
                    vm.current_markers.push([marker['lat'], marker['lng']]);
                });
            }
        }

        function zoomToFit() {

            if (!vm.sightings || !vm.current_markers) {
                return;
            }
            if (vm.current_markers.length === 0) {
                vm.current_markers.push([vm.map.maxbounds.northEast.lat, vm.map.maxbounds.northEast.lng],
                    [vm.map.maxbounds.southWest.lat, vm.map.maxbounds.southWest.lng]);
            }
            vm.mapBounds = new L.latLngBounds(vm.current_markers);
            leafletData.getMap('mapLeaflet').then(function (map) {
                map.fitBounds(vm.mapBounds, {padding: [30, 30]});
            });
        }

        function showPaths() {
            if (!vm.sightings || !vm.map.paths) {
                return;
            }
            var weight = vm.pathsOn ? 3 : 0;
            var opacity = vm.pathsOn ? 0.9 : 0;
            angular.forEach(vm.map.paths, function (path) {
                path['weight'] = weight;
                path['fillOpacity'] = opacity;
            });
        }

        function togglePathsOn() {
            vm.pathsOn = !vm.pathsOn;
        }

        Array.prototype.extend = function (other_array) {
            /* should include a test to check whether other_array really is an array... */
            other_array.forEach(function (v) {
                this.push(v)
            }, this);
        }
    }
})();