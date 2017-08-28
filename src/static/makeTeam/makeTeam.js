'use strict'

angular.module('myApp.makeTeam', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider
    .when('/makeTeam', {
      templateUrl: 'static/makeTeam/makeTeam.html',
      controller: 'makeTeamController',
      access: {restricted: true}
    });
}])
.controller('makeTeamController',
  ['$scope', '$location','$log', '$http','$filter','AuthService',
  function ($scope, $location, $log, $http,$filter,AuthService) {

    $scope.disabled = false;
    var getEmail= function(){
      $scope.disabled=true;
      $http.post('/api/get_email/')
                .then(function(response) {
                  $scope.disabled = false;
                  $log.log("User Email:");
                  $log.log(response.data);
                  $scope.teamForm.ngEmail=response.data;
                }).
                catch(function(response) {
                  $scope.disabled = false;
                  $log.log(response.data);
                  $scope.resultText="error registering pool.";
                });
    };

    $scope.register = function() {

        $scope.disabled = true;

        $log.log("Registering Team:");
        $log.log(                {
                      name:$scope.teamForm.ngName,
                      email:$scope.teamForm.ngEmail,
                      codeword:$scope.teamForm.ngPassword
                    });
        $http.post('/api/create_team/',
                  $.param(
                    {
                      name:$scope.teamForm.ngName,
                      email:$scope.teamForm.ngEmail,
                      codeword:$scope.teamForm.ngPassword
                    }
                  ),
                  {headers: {'Content-Type': 'application/x-www-form-urlencoded'}})

          .then(function(response) {
            $scope.disabled = false;
            $log.log("Registration response:");
            $log.log(response.data);
            $scope.resultText=response.data;
            alert("You have created a team called '" + String($scope.teamForm.ngName) + "' and codeword '" + String($scope.teamForm.ngPassword) + "'. Ready to make your first event?");
            $location.path('/makePool');
          }).
          catch(function(response) {
            $scope.disabled = false;
            if (response.status==409){
              $scope.resultText="Team with that name already exists!";
              $log.log(response.data);
            }
            else{
              $log.log(response.data);
              $scope.resultText="Error registering team.";
            }

          });
      };
    getEmail();

}]);