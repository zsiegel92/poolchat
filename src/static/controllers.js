
angular.module('myApp').controller('loginController',
  ['$scope', '$location', 'AuthService',
  function ($scope, $location, AuthService) {

    $scope.login = function () {

      // initial values
      $scope.error = false;
      $scope.disabled = true;
      // call login from service
      AuthService.login($scope.loginForm.email, $scope.loginForm.password, $scope.loginForm.remember_me)
        // handle success
        .then(function () {
          $location.path('/');
          $scope.disabled = false;
          $scope.loginForm = {};
        })
        // handle error
        .catch(function () {
          $scope.error = true;
          $scope.errorMessage = "Invalid username and/or password";
          $scope.disabled = false;
          $scope.loginForm = {};
        });

    };

}]);


angular.module('myApp').controller('navController',
  ['$scope', '$location', '$http','AuthService',
  function ($scope, $location, $http,AuthService) {

    $scope.navClass = function (page) {
        var currentRoute = $location.path().substring(1) || 'index';
        return page === currentRoute ? 'active' : '';
    };

    $scope.logout = function () {
      $http.post('/api/logout/').then(function(response){
        // $log.log(response);
        $location.path('/login');
      })
      .catch(function(response){
        // $log.log(response);
        // $location.path('/login');
      });
    };

    $scope.triggers = function() {
      $location.path('/triggers');
    };
    $scope.register = function() {
      $location.path('/register');
    };
    // TODO: create "view my pools" button
    $scope.viewPool = function() {
      $location.path('/viewPool/');
    };

}]);

angular.module('myApp').controller('logoutController',
  ['$scope', '$location', 'AuthService',
  function ($scope, $location, AuthService) {

    $scope.logout = function () {
      // call logout from service
      AuthService.logout()
        .then(function () {
          $location.path('/login');
        });
    };
    $scope.logout();

}]);



angular.module('myApp').controller('makeTeamController',
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


angular.module('myApp').controller('makePoolController',
  ['$scope', '$location','$log', '$http','$filter','AuthService',
  function ($scope, $location, $log, $http,$filter,AuthService) {

    // $log.log("tomorrow is: ");
    // $log.log(relativeDateText(1));
    var relativeDateText = function(rel,format) {
      let date = new Date();
      date.setDate(date.getDate() + rel);
      return $filter('date')(date,format|| 'MM-dd-yyyy')
    };
    var relativeDateTime = function(rel,format) {
      let date = new Date();
      date.setDate(date.getDate() + rel);
      return date
    };

    var getEmail= function(){
      $scope.disabled=true;
      $http.post('/api/get_email/')
                .then(function(response) {
                  $scope.disabled = false;
                  $log.log("User Email:");
                  $log.log(response.data);
                  $scope.poolForm.ngEmail=response.data;
                }).
                catch(function(response) {
                  $scope.disabled = false;
                  $log.log(response.data);
                  $scope.resultText="error registering pool.";
                });
    };


    $scope.disabled = false;
    $scope.address_confirmed=false;

    $scope.now =new Date();
    $scope.minNumberDays=3;
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
          // $scope.resultText=response.data.message;
          // $scope.teams=response.data.team_names;
          // $scope.team_ids = response.data.team_ids;

          // Array containing teams as {name:,id:,email:}
          $scope.teams=response.data.teams;
          // object as {id:,email:}
          $scope.self=response.data.self;
          $scope.message = response.data.makePoolMessage;
          $scope.resultText = response.data.makePoolMessage;


          $scope.teamSelection = [];
          $scope.teamSelection_ids=[];
          $scope.poolForm.selectedTeams = {};
          for (i=0; i< $scope.teams.length;i++){
            $scope.poolForm.selectedTeams[String(i)]=true;
            $scope.teamSelection_ids[i]=$scope.teams[i].id;
            $scope.teamSelection[i]=$scope.teams[i].name;
          }
        }).
        catch(function(response) {
          $log.log(response.data);
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
    var dateTime=$filter('date')($scope.initial.ngTime,'MM-dd-yyyy HH:mm');


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

  $scope.getTeams();
  getEmail();

}]);


angular.module('myApp').controller('registerController',
  ['$scope', '$location', '$log','AuthService',
  function ($scope, $location,$log, AuthService) {

    $scope.register = function () {

      // initial values
      $scope.error = false;
      $scope.disabled = true;
      // $log.log([$scope.registerForm.ngFirst,$scope.registerForm.ngLast,$scope.registerForm.ngEmail,$scope.registerForm.ngPassword,$scope.registerForm.ngConfirm_password,$scope.registerForm.ngAccept_tos]);

      // call register from service
      AuthService.register($scope.registerForm.ngFirst,$scope.registerForm.ngLast,$scope.registerForm.ngEmail,$scope.registerForm.ngPassword,$scope.registerForm.ngConfirm_password,$scope.registerForm.ngAccept_tos)
        // handle success
        .then(function () {
          $location.path('/login');
          $scope.disabled = false;
          $scope.registerForm = {};
        })
        // handle error
        .catch(function () {
          $scope.error = true;
          $scope.errorMessage = "Something went wrong!";
          $scope.disabled = false;
          $scope.registerForm = {};
        });

    };

}]);


angular.module('myApp').controller('viewPoolController',
  ['$scope', '$location', 'AuthService','$route', '$routeParams','$log','$http','$window',
  function ($scope, $location, AuthService,$route,$routeParams,$log,$http,$window) {

    $scope.getPoolInfoForUser = function() {
      $log.log("Getting pool info");
      $http.post('api/get_pool_info_for_user')
        .then(function(response){
          $scope.teams = response.data.teams;
          $scope.joined_pools = response.data.joined_pools;
          $scope.eligible_pools = response.data.eligible_pools;
          $scope.carpooler = response.data.carpooler;

          if ($scope.eligible_pools.length >0){
            $log.log("There is an eligible pool!");
            $scope.joinForm.ngPool=0;
          }
          else{
            $log.log("There are no eligible pools!");
          }
          $log.log("Successfully queried for teams, joined_pools, and eligible_pools!");
          $log.log(response.data);
       })
        .catch(function(response) {
          $log.log("Error in getPoolInfo calling api/get_pool_info API");
        });
    };

  $scope.getPoolInfoForUser();

  //route: '/joinPool/:id/name/:name/address/:address/date/:date/time/:time/email/:email/notice/:notice/latenessWindow/:latenessWindow'
  $scope.goto_join = function(){
    var pool = $scope.eligible_pools[$scope.joinForm.ngPool];
    var cp = $scope.carpooler;

    var f= $window.encodeURIComponent;
    var pth = '/joinPool/' + f(pool.id) +'/name/'+ f(pool.name) + '/address/' + f(pool.address) + '/date/' + f(pool.date) + '/time/' + f(pool.time) + '/dateTime/' + f(pool.dateTime) + '/email/' + f(pool.email) + '/notice/' + f(pool.fireNotice) + "/latenessWindow/" + f(pool.latenessWindow) +"/carpooler/cpname/" + f(cp.name) + '/cpfirst/' + f(cp.first) + '/cplast/' + f(cp.last) + '/cpemail/' + f(cp.email);
    $log.log(pth);
    // $log.log($window.encodeURIComponent(pth));
    // $location.path($window.encodeURIComponent(pth));
    $location.path(pth);
  };

}]);

angular.module('myApp').controller('joinPoolController',['$scope', '$location', 'AuthService','$route', '$routeParams','$log','$http','$filter','$window','$q',
  function ($scope, $location, AuthService,$route,$routeParams,$log,$http,$filter,$window,$q){

    var f = $window.decodeURIComponent;
    var r = $routeParams;
    $scope.address_confirmed=false;
    $scope.disabled=false;

    $scope.pool = {'id':f(r.id),'name':f(r.name),'address':f(r.address),'date':f(r.date),'time':f(r.time),'dateTime':f(r.dateTime),'email':f(r.email),'notice':f(r.notice),'latenessWindow':f(r.latenessWindow)};
    $scope.carpooler = {'name':f(r.cpname),'first':f(r.cpfirst),'last':f(r.cplast),'email':f(r.cpemail)};
    // $scope.zoneOffset = $scope.pool.dateTime.getTimezoneOffset();
    // var pool_dateTime = new Date(Date.parse($scope.pool.dateTime));
    // $scope.zoneOffset = pool_dateTime.getTimezoneOffset();

    $scope.preTime = function(baseTimeString,preWindow){
      let dt = new Date(Date.parse(baseTimeString));
      let relDt = new Date(dt.getTime() - preWindow*60*1000);
      return relDt;
    };
    $scope.preTimes = [15,20,25,30,35,40,45,50,55,60];

    $scope.backto_view = function(){
      $location.path('/viewPool');
    };

    // Returns: {'formatted_address':fa,'image_url':iu}
    var conf_address = function(address){
      $scope.disabled = true;

      return $http.post('/api/confirm_address/',
            $.param(
              {
                address:address
              }
            ),
            {headers: {'Content-Type': 'application/x-www-form-urlencoded'}})
        .then(function(response) {
          $scope.disabled = false;

          $log.log({'image_url':response.data.image_url,'formatted_address':response.data.formatted_address});

            return {'image_url':response.data.image_url,'formatted_address':response.data.formatted_address};
            // return response.data;

        }).
        catch(function(response) {
          $scope.disabled = false;
          $log.log(response.data);
          return "error";
        });
    };
    conf_address($scope.pool.address).then((response)=>{
     $scope.pool_info = response;
   });

   $scope.confirmAddress = function(){
    conf_address($scope.tripForm.ngAddress).then((response)=>{
          $scope.address_confirmed=true;
          $scope.tripForm.ngAddress=response.formatted_address;
          $scope.trip_image_url=response.image_url;
    });
   };

  $scope.joinTrip = function() {

    $scope.disabled = true;

    $log.log("Registering:");
    $log.log(                {
                  address:$scope.tripForm.ngAddress,
                  num_seats:$scope.tripForm.ngNumSeats,
                  preWindow:$scope.tripForm.ngPreWindow,
                  on_time:$scope.tripForm.ngOn_time,
                  must_drive:$scope.tripForm.ngMust_drive,
                  pool_id:$scope.pool.id
                });
    $http.post('/api/create_trip/',
              $.param(
                {
                  address:$scope.tripForm.ngAddress,
                  num_seats:$scope.tripForm.ngNumSeats,
                  preWindow:$scope.tripForm.ngPreWindow,
                  on_time:$scope.tripForm.ngOn_time,
                  must_drive:$scope.tripForm.ngMust_drive,
                  pool_id:$scope.pool.id
                }
              ),
              {headers: {'Content-Type': 'application/x-www-form-urlencoded'}})

      .then(function(response) {
        $scope.disabled = false;
        $log.log("Registration response:");
        $log.log(response.data);
        $scope.resultText=response.data;

      }).
      catch(function(response) {
        $scope.disabled = false;
        if (response.status==409){
          $scope.resultText="Redundant entry!";
          $log.log(response.data);
        }
        else{
          $log.log(response.data);
          $scope.errorMessage = response.data;
          $scope.resultText="Error registering Trip.";
        }
      });
  };

}]);




angular.module('myApp').controller('triggerController',
  ['$scope', '$location', 'AuthService',
  function ($scope, $location, AuthService) {
    $scope.resultText=undefined;

    $scope.getResult = function () {
    };
    $scope.clearScope = function() {
    };
    $scope.dropTabs = function() {
    };
    $scope.getPoolInfo = function() {
    };
    $scope.doGroupThere = function() {
    };
    $scope.repeatGroupThere = function() {
    };
    $scope.sendSomeEmails = function() {
    };
    $scope.sendAllEmails = function() {
    };
    $scope.clearScope = function() {
    };

}]);










angular.module('myApp').controller('joinTeamController',
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

  $scope.join = function() {
    $scope.disabled = true;

    $log.log("joining team " + $scope.joinForm.ngTeam);
    $log.log("codeword: " + $scope.joinForm.ngCodeword);

    $http.post('/api/join_team/',
              $.param(
                {
                  teamname:$scope.joinForm.ngTeam,
                  codeword:$scope.joinForm.ngCodeword
                }
              ),
              {headers: {'Content-Type': 'application/x-www-form-urlencoded'}})

      .then(function(response) {
        $scope.disabled = false;
        $log.log("Joined team!");
        $log.log(response.data);
        $scope.resultText=response.data;
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

}]);



angular.module('myApp').controller('approveTeamJoinController',
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
