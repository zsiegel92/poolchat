'use strict'

angular.module('myApp.register', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider
    .when('/register/:email?', {
      templateUrl: 'static/register/register.html',
      controller: 'registerController',
      access: {restricted: false}
    });
}])
.controller('registerController',
  ['$scope', '$location', '$log','AuthService','$window','$routeParams',
  function ($scope, $location,$log, AuthService,$window,$routeParams) {
    var f = $window.decodeURIComponent;
    var r = $routeParams;
    $scope.registerFormValues ={};
    if (r.email){
      $scope.registerFormValues.ngEmail=f(r.email);
    }
    $scope.register = function () {

      // initial values
      $scope.error = false;
      $scope.disabled = true;
      // $log.log([$scope.registerForm.ngFirst,$scope.registerForm.ngLast,$scope.registerForm.ngEmail,$scope.registerForm.ngPassword,$scope.registerForm.ngConfirm_password,$scope.registerForm.ngAccept_tos]);

      // call register from service
      AuthService.register($scope.registerFormValues.ngFirst,$scope.registerFormValues.ngLast,$scope.registerFormValues.ngEmail,$scope.registerFormValues.ngPassword,$scope.registerFormValues.ngConfirm_password,$scope.registerFormValues.ngAccept_tos)
        // handle success
        .then(function (response) {
          $scope.disabled = false;
          if (response.status==200){
            alert("An email has been sent to " + $scope.registerFormValues.ngEmail + ". Please click the link to confirm your account and start using GroupThere.");
            $location.path('/login/' + String($scope.registerFormValues.ngEmail));
        }
        else{
          $scope.registerFormValues.ngPassword='';
          $scope.registerFormValues.ngConfirm_password='';
          $scope.registerFormValues.ngAccept_tos =false;
          $scope.errorMessage=response.data;
        }
        })
        // handle error
        .catch(function (response) {
          $scope.error = true;
          $scope.errorMessage = response.data;
          $scope.disabled = false;
          $scope.registerFormValues.ngPassword='';
          $scope.registerFormValues.ngConfirm_password='';
          $scope.registerFormValues.ngAccept_tos =false;
          $scope.errorMessage=response.data;
        });

    };

}]);
