'use strict'

angular.module('myApp.forgotPasswordChange', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider
    .when('/forgotPasswordChange/:email/:token', {
      templateUrl: 'static/forgotPasswordChange/forgotPasswordChange.html',
      controller: 'forgotPasswordChangeController',
      access: {restricted: false}
    });
}])
.controller('forgotPasswordChangeController',
  ['$scope', '$location', 'AuthService','$route', '$routeParams','$log','$http','$window',
  function ($scope, $location, AuthService,$route,$routeParams,$log,$http,$window) {

    $scope.disabled = false;
    var dec = $window.decodeURIComponent;
    var rp = $routeParams;

    var token = dec(rp.token);
    $scope.email = dec(rp.email);
    $scope.disabled=false;

    $scope.change_pass = function(){
      $scope.disabled = true;

      return $http.post('/api/reset_email/'+String(token),
            $.param(
              {
                password:$scope.changePassFormValues.ngPassword,
                confirm:$scope.changePassFormValues.ngConfirm
              }
            ),
            {headers: {'Content-Type': 'application/x-www-form-urlencoded'}})
        .then(function(response) {
          $scope.disabled = false;
          $scope.resultText=response.data;
          if (response.status==200){
            $scope.successMessage ="Email confirmed! Start using GroupThere now!";
            alert("Password changed! Please log in as " + String($scope.email));
            $location.path('/login/' + String($scope.email));
          }
          else{
            alert("Something went wrong! Please request another password change.");
            $scope.errorMessage=response.data;
            $log.log(response.data);
            $location.path('/forgotPassword')
          }
        }).
        catch(function(response) {
          alert("Something went wrong! Please request another password change.");
          $scope.errorMessage=response.data;
          $log.log(response.data);
          $location.path('/forgotPassword')
        });
    };


}]);
