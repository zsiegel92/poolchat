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
        .then(function (response) {
          $scope.disabled = false;
          if (response.status==200){
            alert("An email has been sent to " + $scope.registerForm.ngEmail + ". Please click the link to confirm your account and start using GroupThere.");

            $scope.registerForm = {};
            $location.path('/login');
        }
        else{
          $scope.registerForm.ngPassword='';
          $scope.registerForm.ngConfirm_password='';
          $scope.registerForm.ngAccept_tos =false;
          $scope.errorMessage=response.data;
        }
        })
        // handle error
        .catch(function (response) {
          $scope.error = true;
          $scope.errorMessage = response.data;
          $scope.disabled = false;
          $scope.registerForm.ngPassword='';
          $scope.registerForm.ngConfirm_password='';
          $scope.registerForm.ngAccept_tos =false;
          $scope.errorMessage=response.data;
        });

    };

}]);
