'use strict'

angular.module('myApp.makePool', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider
  .when('/makePool', {
    templateUrl: 'static/makePool/makePool.html',
    controller: 'makePoolController',
    access: {restricted: true}
  });
}])

.controller('makePoolController',
            ['$scope', '$location','$log', '$http','$filter','AuthService','$rootScope',
            function ($scope, $location, $log, $http,$filter,AuthService,$rootScope) {
              $log.log('in makePool.js');

              $scope.presetting=false;
    // $log.log("tomorrow is: ");
    // $log.log(relativeDateText(1));
    var relativeDateText = function(rel,format) {
      let date = new Date();
      date.setDate(date.getDate() + rel);
      return $filter('date')(date,format|| 'MM-dd-yyyy');
    };
    var relativeDateTime = function(rel,format) {
      let date = new Date();
      date.setDate(date.getDate() + rel);
      return date;
    };






    $scope.disabled = false;
    $scope.address_confirmed=false;

    $scope.now =new Date();
    $scope.minNumberDays=2;
    $scope.minDate = relativeDateTime($scope.minNumberDays);
    $scope.nextYear=relativeDateTime(365);

    // $scope.poolForm.ngTime=new Date(1970, 0, 1, 14, 57, 0);
    $scope.initial={ngTime:new Date(2017, 0, 1, 19, 30, 0),ngDate:$scope.minDate};


    $scope.teams = ['team1', 'team2', 'team3'];
    $scope.team_ids=[1,2,3];

    // Selected teams
    $scope.teamSelection = [];
    $scope.teamSelection_ids=[];
    $scope.teamForms=[];


    // $scope.poolForm.ngDate = new Date();

    // Toggle selection for a given fruit by name
    $scope.toggleSelection = function toggleSelection(team) {
      var idx = $scope.teamSelection.indexOf(team.name);

      // Is currently selected
      if (idx > -1) {
        $scope.teamSelection.splice(idx, 1);
        $scope.teamSelection_ids.splice(idx,1);
      }

      // Is newly selected
      else {
        $scope.teamSelection.push(team.name);
        $scope.teamSelection_ids.push(team.id);
      }
    };

    $scope.getTeams = function() {

      $log.log("Getting user's teams");

      // get the number of generic participants from the input

      // fire the API request
      // returns: {'team_names':team_names,'team_ids':team_ids,'message':message,}
      $http.post('/api/get_teams/')
      .then(function(response) {
        $log.log("Teams for user:");
        $log.log(response.data);
        $log.log("http request successful");
        return response;
      })
      .then(function(response) {
        $scope.teams=response.data.teams;

        $scope.self=response.data.self;
        $scope.message = response.data.makePoolMessage;
        $scope.resultText = response.data.makePoolMessage;

        $scope.teamSelection = [];
        $scope.teamSelection_ids=[];
        $scope.poolForm.selectedTeams = {};
        for (var i=0; i< $scope.teams.length;i++){
          $scope.poolForm.selectedTeams[String(i)]=true;
          $scope.teamSelection_ids[i]=$scope.teams[i].id;
          $scope.teamSelection[i]=$scope.teams[i].name;
        }
      })
      .catch(function(error) {
          // Note: if exception thrown in second .then, response will be undefined.
          $log.log("ERROR in /api/get_teams/ request");
          $log.log(error);
          $scope.resultText="error obtaining teams.";
        });
    };
    $scope.confirmAddress = function() {
      $scope.disabled = true;
      $log.log("Confirming Address");

      // get the number of generic participants from the input

      // fire the API request
      // returns: {'team_names':team_names,'team_ids':team_ids,'message':message,}
      $http.post('/api/confirm_address/',
                 $.param(
                 {
                  address:$scope.poolForm.ngAddress
                }
                ),
                 {headers: {'Content-Type': 'application/x-www-form-urlencoded'}})
      .then(function(response) {
        $scope.disabled = false;
        $log.log("Confirmed address!");
        $log.log(response.data);
        $scope.resultText="Confirmed address!";
        $scope.poolForm.ngAddress=response.data.formatted_address;
        $scope.image_url=response.data.image_url;
        $scope.address_confirmed=true;
      }).
      catch(function(response) {
        $scope.disabled = false;
        $log.log(response.data);
        $scope.resultText="error confirming address.";
      });
    };




    $scope.register = function() {
      $scope.initial.ngTime.setDate($scope.initial.ngDate.getDate());
      $scope.initial.ngTime.setMonth($scope.initial.ngDate.getMonth());
      $scope.initial.ngTime.setFullYear($scope.initial.ngDate.getFullYear());
      var dateTime=$filter('date')($scope.initial.ngTime,'MM-dd-yyyy HH:mm Z');


      $scope.disabled = true;

      $log.log("Registering:");
      $log.log(                {
        name:$scope.poolForm.ngName,
        address:$scope.poolForm.ngAddress,
        dateTimeText:dateTime,
        email:$scope.poolForm.ngEmail,
        fireNotice:$scope.poolForm.ngFireNotice,
        latenessWindow:$scope.poolForm.ngLatenessWindow,
        team_ids:angular.toJson($scope.teamSelection_ids),
        teams:$scope.teamSelection,
        teams2:$scope.poolForm.selectedTeams
      });
      $http.post('/api/create_pool/',
                 $.param(
                 {
                  name:$scope.poolForm.ngName,
                  address:$scope.poolForm.ngAddress,
                  dateTimeText:dateTime,
                  email:$scope.poolForm.ngEmail,
                  fireNotice:$scope.poolForm.ngFireNotice,
                  latenessWindow:$scope.poolForm.ngLatenessWindow,
                  team_ids:angular.toJson($scope.teamSelection_ids)
                }
                ),
                 {headers: {'Content-Type': 'application/x-www-form-urlencoded'}})

      .then(function(response) {
        var baseURL = $location.$$absUrl.replace($location.$$url, '');
    // $scope.fullURL = $location.$$absUrl;
    $scope.disabled = false;
    $log.log("Registration response::");
    $log.log(response.data);
    $scope.resultText=response.data;
    alert("You have created this event, but you are NOT an atendee until you register! You're on your way there now ("+ baseURL + '/viewPool/)');
    $location.path('/viewPool');

  }).
      catch(function(response) {
        $scope.disabled = false;
        if (response.status==409){
          $scope.resultText="Pool with that name already exists!";
          $log.log(response.data);
        }
        else{
          $log.log(response.data);
          $scope.resultText="Error registering Pool.";
        }
      });
    };



  // Called in ng-init of $poolForm.ngEmail
  $scope.setEmail=function(){
    AuthService.requestMyEmail()
    .then(function(){
      $rootScope.myEmail=AuthService.getMyEmail();
      $scope.poolForm.ngEmail= $rootScope.myEmail;
    });
  };

  $scope.getTeams();


}]);


