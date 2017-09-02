'use strict'


var myApp = angular.module('myApp', ['ngRoute','myApp.makePool','myApp.joinPool','myApp.joinTeam','myApp.login','myApp.viewPool','myApp.makeTeam','myApp.register','myApp.approveTeamJoin','myApp.logout','myApp.nav','myApp.triggers','myApp.confirmEmail','myApp.forgotPassword','myApp.forgotPasswordChange','myApp.confirmTeamEmail','myApp.adminApproveTeam'])



.directive('convertToNumber', function() {
  return {
    require: 'ngModel',
    link: function(scope, element, attrs, ngModel) {
      ngModel.$parsers.push(function(val) {
        return parseInt(val, 10);
      });
      ngModel.$formatters.push(function(val) {
        return '' + val;
      });
    }
  };
})
.config(function ($routeProvider,$httpProvider) {
  $httpProvider.defaults.withCredentials = true;
  $routeProvider
    // .when('/', {
    //   access: {restricted: false},
    //   controller: 'navController',
    //   templateUrl: 'static/partials/home.html'
    // })
    .otherwise({
      redirectTo: '/'
    });
});

myApp.filter('relativedate', ['$filter', function ($filter) {
  return function (rel, format) {
    let date = new Date();
    date.setDate(date.getDate() + rel);
    return $filter('date')(date, format || 'MM-dd-yyyy')
  };
}]);

myApp.filter('yesNo', function() {
    return function(input) {
        return input ? 'yes' : 'no';
    }
});
// usage: {{array | joinBy,', '}}
myApp.filter('joinBy', function () {
        return function (input,delimiter) {
            return (input || []).join(delimiter || ',');
        };
    });


myApp.filter('relativeFromTime', ['$filter', function ($filter) {
  return function (rel,time, format) {
    var copy = new Date(time.getTime());
    copy.setHours(copy.getHours() + rel);
    return $filter('date')(copy, format || 'hh:mma')
  };
}]);


myApp.filter('relativeFromMins', ['$filter', function ($filter) {
  return function (rel,time, format) {
    var copy = new Date(time.getTime());
    copy.setMinutes(copy.getMinutes() + rel);
    return $filter('date')(copy, format || 'hh:mma')
  };
}]);

myApp.filter('relativeFromDate', ['$filter', function ($filter) {
  return function (rel,date,time, format) {
    var copy = new Date(date.getTime());
    copy.setHours(time.getHours() + rel);
    copy.setMinutes(time.getMinutes());
    return $filter('date')(copy, format || 'mediumDate')
  };
}]);


myApp.run(function ($rootScope, $location, $route, AuthService) {
  $rootScope.$on('$routeChangeStart',
    function (event, next, current) {
      AuthService.getUserStatus()
      .then(function(){
        var logged_in = AuthService.isLoggedIn();
        $rootScope.logged_in = logged_in;
        if (!logged_in && next && next.access.restricted){
          $location.path('/login');
          $route.reload();
        }
      });
  });
});
