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
  ['$scope', '$location', 'AuthService','$log',
  function ($scope, $location, AuthService,$log) {

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
        .then(function (response) {
          $scope.disabled = false;
          if(response.status === 200){
            $scope.loginForm = {};
            $location.path('/');
          } else {
            $log.log(response.data);
            $scope.loginForm.password='';
            $scope.loginForm.remember_me=false;
            $scope.error = true;
            $scope.errorMessage = response.data;
          }

        })
        // handle error
        .catch(function (response) {
          $scope.error = true;
          $scope.errorMessage = response.data;
          $scope.disabled = false;
          $scope.loginForm.password='';
          $scope.loginForm.remember_me=false;
        });

    };

}]);
