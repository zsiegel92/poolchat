'use strict'

angular.module('myApp.login', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider
    .when('/login', {
      templateUrl: 'static/login/login.html',
      controller: 'loginController',
      access: {restricted: false}
    });
}])

.controller('loginController',
  ['$scope', '$location', 'AuthService',
  function ($scope, $location, AuthService) {

    $scope.goto_register = function (){
      $location.path('/register');
    };
    $scope.login = function () {

      // initial values
      $scope.error = false;
      $scope.disabled = true;
      // call login from service
      AuthService.login($scope.loginForm.email, $scope.loginForm.password, $scope.loginForm.remember_me)
        // handle success
        .then(function () {
          $location.path('/');
          $scope.disabled = false;
          $scope.loginForm = {};
        })
        // handle error
        .catch(function () {
          $scope.error = true;
          $scope.errorMessage = "Invalid username and/or password";
          $scope.disabled = false;
          $scope.loginForm = {};
        });

    };

}]);
