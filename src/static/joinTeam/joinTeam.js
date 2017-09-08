'use strict'

angular.module('myApp.joinTeam', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider
    .when('/joinTeam', {
      templateUrl: 'static/joinTeam/joinTeam.html',
      controller: 'joinTeamController',
      access: {restricted: true}
    });
}])
.controller('joinTeamController',
  ['$scope', '$location','$log', '$http','$filter','AuthService',
  function ($scope, $location, $log, $http,$filter,AuthService) {



    $scope.disabled = false;
    // $scope.baseURL = $location.$$absUrl.replace($location.$$url, '');
    // $scope.fullURL = $location.$$absUrl;

    // $scope.teams = ['team1', 'team2', 'team3'];
    // $scope.team_ids=[1,2,3];


    $scope.getTeams = function() {

      $log.log("Getting user's teams");

      // get the number of generic participants from the input

      // fire the API request
      // returns: {'team_names':team_names,'team_ids':team_ids,'message':message,}
      $http.post('/api/get_teams/')
        .then(function(response) {
          $log.log("Foreign Teams:");
          $log.log(response.data);
          $scope.resultText=response.data.message;
          $scope.my_id = response.data.self.id;
          // $scope.foreignTeams=response.data.foreign_team_names;
          // $scope.foreignTeam_ids = response.data.foreign_team_ids;
          // $scope.teams = response.data.team_names;
          // $scope.team_ids = response.data.team_ids;
          // $scope.team_emails = response.data.team_emails;

          // teams is list of {'name':,'id':,'email':}
          // foreignTeams is list of {'name':,'id':}
          $scope.teams = response.data.teams;
          $scope.foreignTeams= response.data.foreign_teams;
        }).
        catch(function(response) {
          $log.log(response.data);
          $scope.resultText="error obtaining teams.";
        });
    };

  $scope.access_request_feedback={};
  $scope.request_access = function(team_id){
    $scope.disabled=true;
    $http.post('/api/request_team_codeword/teamId/' + String(team_id))
    .then(function(response){
      $scope.disabled=false;
      $scope.access_request_feedback[team_id]=response.data;
    })
    .catch(function(response){
      $scope.disabled=false;
      $scope.access_request_feedback[team_id]=response.data;
    });
  };

  $scope.open_foreign = function(){
    var idx = $scope.joinFormValues.ngTeam;
    $log.log("Attempting to expand element " + String(idx));
    var el=undefined;
    for (var i = 0; i < $scope.foreignTeams.length; i++){
      if (i != idx){
        el = angular.element( document.querySelector( '#foreign_collapse' + String(i) ) );
        if (el.hasClass('in')) { // hidden
          $(el).collapse('hide');
        }
      }
    }

    var myEl = angular.element( document.querySelector( '#foreign_collapse' + String(idx) ) );
    if (!angular.element(myEl).hasClass('in')) { // hidden
          $(myEl).collapse('show');
          // myEl.addClass('in');
        }
  };

  $scope.joinFormValues={};
  $scope.join = function() {
    $scope.disabled = true;
    // value changed from {{foreignTeam.name}} to {{$index}}
    var newName = $scope.foreignTeams[$scope.joinFormValues.ngTeam].name;
    $log.log("joining team " + newName);
    $log.log("codeword: " + $scope.joinFormValues.ngCodeword);

    $http.post('/api/join_team/',
              $.param(
                {
                  teamname:newName,
                  codeword:$scope.joinFormValues.ngCodeword
                }
              ),
              {headers: {'Content-Type': 'application/x-www-form-urlencoded'}})

      .then(function(response) {
        $scope.disabled = false;
        $log.log("Joined team!");
        $log.log(response.data);
        $scope.resultText=response.data;
        alert("You have joined the team " + String(newName));
        $scope.joinFormValues.ngCodeword='';
        $scope.getTeams();
      }).
      catch(function(response) {
        $scope.disabled = false;
        if (response.status==401){
          $scope.resultText="Wrong codeword.";
        }
        else{
          $scope.resultText="Database error";
        }

      });
  };

  $scope.getTeams();

  $scope.leave_team = function(ind){
    $scope.disabled=true;
    var leaveTeam = $scope.teams[ind];
    var r = confirm("Are you sure you'd like to leave team " + String(leaveTeam.name) + '?');
    if (r===true){
       $http.post('/api/leave_team/',
                $.param(
                  {
                    team_id:leaveTeam.id
                  }
                ),
                {headers: {'Content-Type': 'application/x-www-form-urlencoded'}})
      .then(function(response){
        var baseURL = $location.$$absUrl.replace($location.$$url, '');
        $scope.disabled = false;
        $scope.resultText=response.data;
        alert("You have left team " + leaveTeam.name + "! "+ leaveTeam.email + " has been notified of the change. Visit " + baseURL + "/joinTeam to manage your teams.");
          $location.path('/joinTeam');
          $scope.getTeams();
      })
      .catch(function(response){
        $scope.disabled=false;
        $log.log(response.data);
        alert("Something went wrong! You are still a member of team " + String() + ". Please try again later if this is unacceptable.");
        $location.path('/joinTeam');
        $scope.getTeams();
      });
    }
    else{

    }

  };






}]);
