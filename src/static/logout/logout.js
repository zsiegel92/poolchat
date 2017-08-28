'use strict'

angular.module('myApp.logout', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider
    .when('/logout', {
      controller: 'logoutController',
      access: {restricted: true}
    });
}])
.controller('logoutController',
  ['$scope', '$location', 'AuthService',
  function ($scope, $location, AuthService) {

    $scope.logout = function () {
      // call logout from service
      AuthService.logout()
        .then(function () {
          $location.path('/login');
        });
    };
    $scope.logout();

}]);
