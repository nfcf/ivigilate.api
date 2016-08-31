(function () {
    'use strict';

    angular
        .module('ivigilate.detectors.controllers')
        .controller('EditDetectorController', EditDetectorController);

    EditDetectorController.$inject = ['$location', '$scope', '$timeout', '$uibModalInstance', 'data', 'Authentication', 'Detectors', 'leafletData', 'leafletMarkerEvents'];

    function EditDetectorController($location, $scope, $timeout, $uibModalInstance, data, Authentication, Detectors, leafletData, leafletMarkerEvents) {
        var vm = this;
        vm.fileChanged = fileChanged;
        vm.cancel = cancel;
        vm.save = save;
        vm.resizeMap = resizeMap;
        vm.zoomToFit = zoomToFit;

        vm.error = undefined;
        vm.detector = undefined;
        vm.imagePreview = undefined;
        vm.imageToUpload = undefined;
        vm.map = undefined;
        vm.showMap = false;
        vm.current_markers = undefined;
        
        vm.patrolOrHomeCareMode = true;
        vm.sosNumber = undefined;
        vm.number1 = undefined;
        vm.number2 = undefined;
        vm.nameCall1 = undefined;
        vm.nameCall2 = undefined;
        
        
        var searchControl = new L.Control.Search({
            url: 'http://nominatim.openstreetmap.org/search?format=json&q={s}',
            jsonpParam: 'json_callback',
            propertyName: 'display_name',
            propertyLoc: ['lat', 'lon'],
            autoCollapse: true,
            autoType: false,
            minLength: 2,
            circleLocation: false
        });
        searchControl.on('search_locationfound', function (e) {
            vm.map.markers['m']['lng'] = e.latlng['lng'];
            vm.map.markers['m']['lat'] = e.latlng['lat'];
        });

        activate();

        function activate() {
            var user = Authentication.getAuthenticatedUser();
            if (user) {
                populateDialog(data);
            }
            else {
                $location.url('/');
            }
        }

        function populateDialog(data) {
            vm.detector = data;
            vm.imagePreview = vm.detector.photo;
            initializeContacts();

            $scope.$watch('vm.detector.type', function () {
                vm.showMap = vm.detector.type == 'F';
            }, true);


            if (!vm.detector.location) {
                vm.detector.location = {
                    'type': 'Point',
                    'coordinates': [-40.70744491, 34.698986644] //Defaults to the middle of the ocean
                };
            }
            vm.map = {
                defaults: {
                    scrollWheelZoom: false
                },
                maxbounds: {'northEast': {'lat': -60, 'lng': -120}, 'southWest': {'lat': 60, 'lng': 120}},
                markers: {
                    'm': {
                        'lng': vm.detector.location.coordinates[0],
                        'lat': vm.detector.location.coordinates[1],
                        'message': vm.detector['type'] + " " + vm.detector['name'] + " with ID: " + vm.detector['uid'],
                        'icon': {
                            'type': 'vectorMarker',
                            'icon': 'map-marker',
                            'markerColor': '#00c6d2'
                        },
                        draggable: true
                    }
                },
                events: {
                    markers: {
                        enable: leafletMarkerEvents.getAvailableEvents()
                    }
                }
            };
            resizeMap();
            //set up map custom controls
            leafletData.getMap('editDetectorMap').then(function (map) {
                L.easyButton('fa-arrows', function () {
                    zoomToFit();
                }).addTo(map);
                map.addControl(searchControl);
            });
        }

        function fileChanged(files) {
            if (files && files[0]) {
                var fileReader = new FileReader();
                fileReader.onload = function (e) {
                    $scope.$apply(function () {
                        vm.imageToUpload = files[0];
                        $timeout(function () {
                            vm.imagePreview = fileReader.result;
                        }, 250);
                    });
                };
                fileReader.readAsDataURL(files[0]);
            } else {
                vm.imagePreview = null;
            }
        }

        function save() {
            $scope.$broadcast('show-errors-check-validity');
            updateContactSettings();

            if (vm.form.$valid) {
                vm.detector.location.coordinates = [vm.map.markers['m']['lng'], vm.map.markers['m']['lat']];
                Detectors.update(vm.detector, vm.imageToUpload).then(successFn, errorFn);
            } else {
                vm.error = 'There are invalid fields in the form.';
            }

            function successFn(data, status, headers, config) {
                $uibModalInstance.close(vm.detector);
            }

            function errorFn(data, status, headers, config) {
                vm.error = data.status != 500 ? JSON.stringify(data.data) : data.statusText;
            }
        }

        function cancel() {
            $uibModalInstance.dismiss('Cancel');
        }

        function zoomToFit() {
            vm.current_markers = [];
            if (!vm.map.markers) {
                vm.current_markers.push([vm.map.maxbounds.northEast.lat, vm.map.maxbounds.northEast.lng],
                    [vm.map.maxbounds.southWest.lat, vm.map.maxbounds.southWest.lng]);
            } else {
                vm.current_markers.push([vm.map.markers.m.lat, vm.map.markers.m.lng]);
            }
            vm.mapBounds = new L.latLngBounds(vm.current_markers);
            leafletData.getMap('editDetectorMap').then(function (map) {
                map.fitBounds(vm.mapBounds, {padding: [50, 50]});
            });
        }

        function resizeMap() {
            leafletData.getMap('editDetectorMap').then(function (map) {
                setTimeout(function () {
                    map.invalidateSize();
                    map.options.minZoom = 1;
                    zoomToFit();
                }, 500);
            });
        }

        $scope.$on('leafletDirectiveMarker.editDetectorMap.dragend', function (e, args) {
            vm.map.markers['m']['lng'] = args.leafletEvent.target._latlng.lng;
            vm.map.markers['m']['lat'] = args.leafletEvent.target._latlng.lat;
            zoomToFit();
        });

        function initializeContacts() {
            if (!vm.patrolOrHomeCareMode || !vm.detector.metadata) {
                return;
            }
            var metadata = JSON.parse(vm.detector.metadata);
            if (metadata['contact_settings']) {
                vm.sosNumber = metadata['contact_settings']['sos_number'] ? metadata['contact_settings']['sos_number'] : '';
                vm.number1 = metadata['contact_settings']['number1'] ? metadata['contact_settings']['number1'] : '';
                vm.number2 = metadata['contact_settings']['number2'] ? metadata['contact_settings']['number2'] : '';
                vm.nameCall1 = metadata['contact_settings']['name_call1'] ? metadata['contact_settings']['name_call1'] : '';
                vm.nameCall2 = metadata['contact_settings']['name_call2'] ? metadata['contact_settings']['name_call2'] : '';
            }
        }

        function updateContactSettings() {
            if (!vm.patrolOrHomeCareMode) {
                return;
            }
            var contact_values = {
                'sos_number': vm.sosNumber,
                'number1': vm.number1,
                'number2': vm.number2,
                'name_call1': vm.nameCall1,
                'name_call2': vm.nameCall2
            };
            var detector_metadata = !vm.detector.metadata ? {} : JSON.parse(vm.detector.metadata);
            if (!detector_metadata['contact_settings']) {
                detector_metadata['contact_settings'] = {};
            }

            angular.forEach(contact_values, function(value, key){
                detector_metadata['contact_settings'][key] = contact_values[key];
            });
            
            vm.detector.metadata = JSON.stringify(detector_metadata);
        }
    }
})();