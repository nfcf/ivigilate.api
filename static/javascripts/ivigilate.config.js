(function () {
    'use strict';

    angular
        .module('ivigilate.config')
        .config(config);

    config.$inject = ['$locationProvider', 'uiGmapGoogleMapApiProvider', 'dialogsProvider', '$translateProvider',
        'stripeProvider', 'showErrorsConfigProvider', 'toastrConfig'];

    /**
     * @name config
     * @desc Enable HTML5 routing
     */
    function config($locationProvider, uiGmapGoogleMapApiProvider, dialogsProvider, $translateProvider,
                    stripeProvider, showErrorsConfigProvider, toastrConfig) {
        $locationProvider.html5Mode(true);
        $locationProvider.hashPrefix('!');

        stripeProvider.setPublishableKey('pk_test_oVCmhvKCeq8opChm22KPvc27');

        showErrorsConfigProvider.showSuccess(true);
        showErrorsConfigProvider.trigger('keypress');

        uiGmapGoogleMapApiProvider.configure({
            //    key: 'your api key',
            v: '3.17',
            libraries: 'places,weather,geometry,visualization'
        });

        dialogsProvider.useBackdrop('static');
        dialogsProvider.useEscClose(true);
        dialogsProvider.useCopy(true);
        //dialogsProvider.setSize('lg');

        $translateProvider.translations('en', {
            just_now: 'just now',
            seconds_ago: '{{time}} seconds ago',
            a_minute_ago: 'a minute ago',
            minutes_ago: '{{time}} minutes ago',
            an_hour_ago: 'an hour ago',
            hours_ago: '{{time}} hours ago',
            a_day_ago: 'yesterday',
            days_ago: '{{time}} days ago',
            a_week_ago: 'a week ago',
            weeks_ago: '{{time}} weeks ago',
            a_month_ago: 'a month ago',
            months_ago: '{{time}} months ago',
            a_year_ago: 'a year ago',
            years_ago: '{{time}} years ago',
            over_a_year_ago: 'over a year ago',
            seconds_from_now: '{{time}} seconds from now',
            a_minute_from_now: 'a minute from now',
            minutes_from_now: '{{time}} minutes from now',
            an_hour_from_now: 'an hour from now',
            hours_from_now: '{{time}} hours from now',
            a_day_from_now: 'tomorrow',
            days_from_now: '{{time}} days from now',
            a_week_from_now: 'a week from now',
            weeks_from_now: '{{time}} weeks from now',
            a_month_from_now: 'a month from now',
            months_from_now: '{{time}} months from now',
            a_year_from_now: 'a year from now',
            years_from_now: '{{time}} years from now',
            over_a_year_from_now: 'over a year from now'
        });

        $translateProvider.translations('pt', {
            just_now: 'agora',
            seconds_ago: 'há {{time}} segundos',
            hours_ago: 'há {{time}} horas'
        });

        $translateProvider.preferredLanguage('en');

        angular.extend(toastrConfig, {
            autoDismiss: false,
            containerId: 'toast-container',
            maxOpened: 0,
            newestOnTop: true,
            positionClass: 'toast-bottom-right',
            preventDuplicates: true,
            preventOpenDuplicates: true,
            target: 'body',

            allowHTML: false,
            closeButton: true,
            timeOut: 30000,
            extendedTimeOut: 30000,
            tapToDismiss: false,
            progressBar: true
        });
    }

})();