'use strict'

angular.module('myApp.login', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider
    .when('/login/:email?', {
      templateUrl: 'static/login/login.html',
      controller: 'loginController',
      access: {restricted: false}
    });
}])
.controller('loginController',
  ['$scope', '$location', 'AuthService','$log','$routeParams','$window',
  function ($scope, $location, AuthService,$log,$routeParams,$window) {
    var f = $window.decodeURIComponent;
    var r = $routeParams;
    $scope.loginFormValues={};
    if (r.email){
      $scope.loginFormValues.email=f(r.email);
    }
    $scope.goto_register = function (){
      $location.path('/register');
    };
    $scope.login = function () {

      // initial values
      $scope.error = false;
      $scope.disabled = true;
      // call login from service
      AuthService.login($scope.loginFormValues.email, $scope.loginFormValues.password, $scope.loginFormValues.remember_me)
        // handle success
        .then(function (response) {
          $scope.disabled = false;
          if(response.status === 200){
            $scope.loginFormValues = {};
            $location.path('/');
          } else {
            $log.log(response.data);
            $scope.loginFormValues.password='';
            $scope.loginFormValues.remember_me=false;
            $scope.error = true;
            $scope.errorMessage = response.data;
          }

        })
        // handle error
        .catch(function (response) {
          $scope.error = true;
          $scope.errorMessage = response.data;
          $scope.disabled = false;
          $scope.loginFormValues.password='';
          $scope.loginFormValues.remember_me=false;
        });

    };

}]);
