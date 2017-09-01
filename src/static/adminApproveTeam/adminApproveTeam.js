// '{base}?#!/admin_approve_team/{team_id}/{team_key}'.format(base=url_base,team_id=team_id,team_key=team_key)
// @app.route('api/admin_approve_team',methods=['POST'])
// @login_required
// def api_admin_approve_team():
// 	team_id=request.values.get('team_id')
// 	team_key=request.values.get('team_key')


'use strict'

angular.module('myApp.adminApproveTeam', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider
    .when('/adminApproveTeam/:team_id/:team_key*', {
      templateUrl: 'static/adminApproveTeam/adminApproveTeam.html',
      controller: 'adminApproveTeamController',
      access: {restricted: true}
    });
}])
.controller('adminApproveTeamController',
  ['$scope', '$location', 'AuthService','$route', '$routeParams','$log','$http','$window',
  function ($scope, $location, AuthService,$route,$routeParams,$log,$http,$window) {

    $scope.disabled = false;
    var dec = $window.decodeURIComponent;
    var rp = $routeParams;

    $scope.confirmed=false;
    $scope.disabled=false;

    $scope.team_key = dec(rp.team_key);
    $scope.team_id = dec(rp.team_id);

  // NOTE: the token (referred to as 'id' in this controller) is a token generated on server, times out.
  var approve = function(address){
      $scope.disabled = true;
      $log.log("Attempting to query /api/admin_approve_team with arguments {team_id: " + String($scope.team_id) + ", team_key: " + String($scope.team_key) +"}");
      return $http.post('/api/admin_approve_team',
            $.param(
              {
                team_id:$scope.team_id,
                team_key:$scope.team_key
              }
            ),
            {headers: {'Content-Type': 'application/x-www-form-urlencoded'}})
        .then(function(response) {
          $scope.disabled = false;
          $scope.result=response.data;
          if (response.status==200){
            $scope.resultText="Team approved!";
            $scope.message= response.data.message;
            alert(String($scope.message));
          }
          else{
            $scope.resultText = "Something went wrong! Email not confirmed.";
            $log.log(response.data);

          }
        }).
        catch(function(response) {
          $scope.disabled = false;
          $log.log(response.data);
          $scope.resultText = "Something went wrong! Email not confirmed.";
	        if (response.data.message){
	        	$scope.message= response.data.message;
	        	alert(String($scope.message));
	        }
        });
    };


  approve();

}]);
