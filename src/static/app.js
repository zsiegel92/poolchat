var myApp = angular.module('myApp', ['ngRoute'])
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
});

myApp.filter('relativedate', ['$filter', function ($filter) {
  return function (rel, format) {
    let date = new Date();
    date.setDate(date.getDate() + rel);
    return $filter('date')(date, format || 'yyyy-MM-dd')
  };
}]);


myApp.filter('relativeFromTime', ['$filter', function ($filter) {
  return function (rel,time, format) {
    var copy = new Date(time.getTime());
    copy.setHours(copy.getHours() + rel);
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

myApp.config(function ($routeProvider,$httpProvider) {
  $httpProvider.defaults.withCredentials = true;
  $routeProvider
    .when('/', {
      access: {restricted: true},
      controller: 'logoutController',
      templateUrl: 'static/partials/home.html'
    })
    .when('/login', {
      templateUrl: 'static/partials/login.html',
      controller: 'loginController',
      access: {restricted: false}
    })
    .when('/logout', {
      controller: 'logoutController',
      access: {restricted: true}
    })
    .when('/register', {
      templateUrl: 'static/partials/register.html',
      controller: 'registerController',
      access: {restricted: false}
    })
    .when('/one', {
      template: '<h1>This is page one!</h1>',
      access: {restricted: true}
    })
    .when('/two', {
      template: '<h1>This is page two!</h1>',
      access: {restricted: false}
    })
    .when('/triggers', {
      templateUrl: 'static/partials/triggers.html',
      controller: 'triggerController',
      access: {restricted: true}
    })
    .when('/viewPool/:poolId?', {
      templateUrl: 'static/partials/viewPool.html',
      controller: 'makePoolController',
      access: {restricted: true}
    })
    .when('/makePool', {
      templateUrl: 'static/partials/makePool.html',
      controller: 'makePoolController',
      access: {restricted: true}
    })
    .otherwise({
      redirectTo: '/'
    });
});

myApp.run(function ($rootScope, $location, $route, AuthService) {
  $rootScope.$on('$routeChangeStart',
    function (event, next, current) {
      AuthService.getUserStatus()
      .then(function(){
        var logged_in = AuthService.isLoggedIn();
        $rootScope.logged_in = logged_in;
        if (next.access.restricted && !logged_in){
          $location.path('/login');
          $route.reload();
        }
      });
  });
});
