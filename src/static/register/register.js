'use strict'

angular.module('myApp.register', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider
    .when('/register', {
      templateUrl: 'static/register/register.html',
      controller: 'registerController',
      access: {restricted: false}
    });
}])
.controller('registerController',
  ['$scope', '$location', '$log','AuthService',
  function ($scope, $location,$log, AuthService) {

    $scope.register = function () {

      // initial values
      $scope.error = false;
      $scope.disabled = true;
      // $log.log([$scope.registerForm.ngFirst,$scope.registerForm.ngLast,$scope.registerForm.ngEmail,$scope.registerForm.ngPassword,$scope.registerForm.ngConfirm_password,$scope.registerForm.ngAccept_tos]);

      // call register from service
      AuthService.register($scope.registerForm.ngFirst,$scope.registerForm.ngLast,$scope.registerForm.ngEmail,$scope.registerForm.ngPassword,$scope.registerForm.ngConfirm_password,$scope.registerForm.ngAccept_tos)
        // handle success
        .then(function () {
          $location.path('/login');
          $scope.disabled = false;
          $scope.registerForm = {};
        })
        // handle error
        .catch(function () {
          $scope.error = true;
          $scope.errorMessage = "Something went wrong!";
          $scope.disabled = false;
          $scope.registerForm = {};
        });

    };

}]);
