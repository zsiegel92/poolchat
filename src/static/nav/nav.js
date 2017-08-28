'use strict'

angular.module('myApp.nav', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider
    .when('/', {
      templateUrl: 'static/nav/home.html',
      controller: 'navController',
      access: {restricted: false}
    });
}])
.controller('navController',
  ['$scope', '$location', '$http','AuthService',
  function ($scope, $location, $http,AuthService) {

    $scope.navClass = function (page) {
        var currentRoute = $location.path().substring(1) || 'index';
        return page === currentRoute ? 'active' : '';
    };

    $scope.logout = function () {
      $http.post('/api/logout/').then(function(response){
        // $log.log(response);
        $location.path('/login');
      })
      .catch(function(response){
        // $log.log(response);
        // $location.path('/login');
      });
    };

    $scope.triggers = function() {
      $location.path('/triggers');
    };
    $scope.register = function() {
      $location.path('/register');
    };
    // TODO: create "view my pools" button
    $scope.viewPool = function() {
      $location.path('/viewPool/');
    };

}]);

