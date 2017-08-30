'use strict'

angular.module('myApp.forgotPassword', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider
    .when('/forgotPassword', {
      templateUrl: 'static/forgotPassword/forgotPassword.html',
      controller: 'forgotPasswordController',
      access: {restricted: false}
    });
}])
.controller('forgotPasswordController',
  ['$scope', '$location', 'AuthService','$route', '$routeParams','$log','$http','$window',
  function ($scope, $location, AuthService,$route,$routeParams,$log,$http,$window) {

    $scope.disabled = false;
    var dec = $window.decodeURIComponent;
    var rp = $routeParams;

    $scope.disabled=false;

    $scope.request_email = function(){
      $scope.disabled = true;

      return $http.post('/api/forgot_password',
            $.param(
              {
                email:$scope.emailFormValues.email
              }
            ),
            {headers: {'Content-Type': 'application/x-www-form-urlencoded'}})
        .then(function(response) {
          $scope.disabled = false;
          $scope.resultText=response.data;
          if (response.status==200){
            $scope.successMessage="Email confirmed! Start using GroupThere now!";
            alert("Please click the link in the email send to " + String($scope.emailFormValues.email));
            $location.path('/login/' + String($scope.emailFormValues.email));
          }
          else{
            $scope.resultText = "Something went wrong! Confirmation email not sent. Please try again, or register a new account.";
            $scope.errorMessage=response.data;
            $scope.resultText = "Something went wrong! Confirmation email not sent. Please try again, or register a new account.";
          }
        }).
        catch(function(response) {
          $scope.disabled = false;
          $scope.errorMessage=response.data;
          $scope.resultText = "Something went wrong! Confirmation email not sent. Please try again, or register a new account.";
        });
    };


}]);
