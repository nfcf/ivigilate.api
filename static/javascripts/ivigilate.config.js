(function () {
    'use strict';

    angular
        .module('ivigilate.config')
        .config(config);

    config.$inject = ['$locationProvider', 'uiGmapGoogleMapApiProvider', 'dialogsProvider', '$translateProvider'];

    /**
     * @name config
     * @desc Enable HTML5 routing
     */
    function config($locationProvider, uiGmapGoogleMapApiProvider, dialogsProvider, $translateProvider) {
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

        $translateProvider.translations('en', {
            just_now: 'just now',
            seconds_ago: '{{time}} seconds ago',
            hours_ago: '{{time}} hours ago'
        });

        $translateProvider.translations('pt', {
            just_now: 'agora',
            seconds_ago: 'há {{time}} segundos',
            hours_ago: 'há {{time}} horas'
        });

        $translateProvider.preferredLanguage('en');
    }

})();