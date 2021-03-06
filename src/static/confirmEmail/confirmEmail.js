'use strict'

angular.module('myApp.confirmEmail', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider
    .when('/confirmEmail/:email/:id', {
      templateUrl: 'static/confirmEmail/confirmEmail.html',
      controller: 'confirmEmailController',
      access: {restricted: false}
    });
}])
.controller('confirmEmailController',
  ['$scope', '$location', 'AuthService','$route', '$routeParams','$log','$http','$window',
  function ($scope, $location, AuthService,$route,$routeParams,$log,$http,$window) {

    $scope.disabled = false;
    var dec = $window.decodeURIComponent;
    var rp = $routeParams;

    $scope.confirmed=false;
    $scope.disabled=false;

    $scope.user_email = dec(rp.email);
    $scope.user_id = dec(rp.id);

  // NOTE: the token (referred to as 'id' in this controller) is a token generated on server, times out.
  var conf_email = function(address){
      $scope.disabled = true;

      return $http.post('/api/confirm_email',
            $.param(
              {
                email:$scope.user_email,
                token:$scope.user_id
              }
            ),
            {headers: {'Content-Type': 'application/x-www-form-urlencoded'}})
        .then(function(response) {
          $scope.disabled = false;
          $scope.result=response.data;
          if (response.status==200){
            $scope.resultText="Email confirmed! Start using GroupThere now!";
            alert("Email confirmed! You have been logged into GroupThere using " + String($scope.user_email));
            $location.path('/');
          } else if (response.status==201){
            $scope.resultText="Email already confirmed.";
            alert("Email already confirmed. For security, you have been logged out of GroupThere. Please login using " + String($scope.user_email));
            $location.path('/login/' + $scope.user_email);
          }
          else{
            $scope.resultText = "Something went wrong! Email not confirmed.";
            $log.log($scope.result);
          }
        }).
        catch(function(response) {
          $scope.disabled = false;
          $log.log(response.data);
          $scope.resultText = "Something went wrong! Email not confirmed.";
        });
    };


  conf_email();

}]);
