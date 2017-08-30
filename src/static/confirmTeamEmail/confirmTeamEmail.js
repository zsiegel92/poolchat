'use strict'

angular.module('myApp.confirmTeamEmail', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider
    .when('/confirmTeamEmail/:email/:id', {
      templateUrl: 'static/confirmTeamEmail/confirmTeamEmail.html',
      controller: 'confirmTeamEmailController',
      access: {restricted: false}
    });
}])
.controller('confirmTeamEmailController',
  ['$scope', '$location', 'AuthService','$route', '$routeParams','$log','$http','$window',
  function ($scope, $location, AuthService,$route,$routeParams,$log,$http,$window) {

    $scope.disabled = false;
    var dec = $window.decodeURIComponent;
    var rp = $routeParams;

    $scope.confirmed=false;
    $scope.disabled=false;

    $scope.team_email = dec(rp.email);
    $scope.team_id = dec(rp.id);

  // NOTE: the token (referred to as 'id' in this controller) is a token generated on server, times out.
  var conf_email = function(address){
      $scope.disabled = true;
      $log.log("Attempting to query /api/confirm_team_email with arguments {email: " + String($scope.team_email) + ", id: " + String($scope.team_id) +"}");
      return $http.post('/api/confirm_team_email',
            $.param(
              {
                email:$scope.team_email,
                id:$scope.team_id
              }
            ),
            {headers: {'Content-Type': 'application/x-www-form-urlencoded'}})
        .then(function(response) {
          $scope.disabled = false;
          $scope.result=response.data;
          if (response.status==200){
            $scope.resultText="Team email confirm!";
            $scope.team_name = response.data.team_name;
            $scope.message= response.data.message;
            alert("Email confirmed! The team " + String($scope.team_name) + " with email " + String($scope.team_email) + " can now be used. " + String($scope.message));
            $location.path('/' + $scope.team_email);
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
