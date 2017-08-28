'use strict'

angular.module('myApp.approveTeamJoin', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider
    .when('/approveTeamJoin/:new_user_id/:team_id', {
      templateUrl: 'static/approveTeamJoin/approveTeamJoin.html',
      controller: 'approveTeamJoinController',
      access: {restricted: true}
    });
}])
.controller('approveTeamJoinController',
  ['$scope', '$location', 'AuthService','$route', '$routeParams','$log','$http','$window',
  function ($scope, $location, AuthService,$route,$routeParams,$log,$http,$window) {

    $scope.disabled = false;
    var dec = $window.decodeURIComponent;
    var rp = $routeParams;
    $scope.address_confirmed=false;
    $scope.disabled=false;

    $scope.new_user_id = dec(rp.new_user_id);
    $scope.team_id = dec(rp.team_id);


  $scope.approve_team = function(){
    $scope.disabled=true;
    $http.post('/api/approve_team/teamId/' + String($scope.team_id) + '/userId/' + String($scope.new_user_id))
    .then(function(response){
      $scope.disabled=false;
      $scope.message=response.data.message;
      $scope.email=response.data.email;
      // email = {from:,to:,body:,subject:}
    })
    .catch(function(response){
      $scope.disabled=false;
      $scope.message = response.data.message;
      $scope.error=response.data;
    });
  };


  $scope.approve_team();

}]);
