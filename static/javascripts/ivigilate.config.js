(function () {
    'use strict';

    angular
        .module('ivigilate.config')
        .config(config);

    config.$inject = ['$locationProvider', 'uiGmapGoogleMapApiProvider', 'dialogsProvider'];

    /**
     * @name config
     * @desc Enable HTML5 routing
     */
    function config($locationProvider, uiGmapGoogleMapApiProvider, dialogsProvider) {
        $locationProvider.html5Mode(true);
        $locationProvider.hashPrefix('!');

        uiGmapGoogleMapApiProvider.configure({
            //    key: 'your api key',
            v: '3.17',
            libraries: 'places,weather,geometry,visualization'
        });

        dialogsProvider.useBackdrop('static');
        dialogsProvider.useEscClose(true);
        dialogsProvider.useCopy(true);
        dialogsProvider.setSize('lg');
    }

})();