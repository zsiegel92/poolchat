
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
  ['$scope', '$location', 'AuthService',
  function ($scope, $location, AuthService) {

    $scope.navClass = function (page) {
        var currentRoute = $location.path().substring(1) || 'index';
        return page === currentRoute ? 'active' : '';
    };




    $scope.logout = function () {
      // call logout from service
      AuthService.logout()
        .then(function () {
          $location.path('/login');
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
    logout();

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
              $scope.resultText="Error registering pool.";
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
      return $filter('date')(date,format|| 'yyyy-MM-dd')
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
    $scope.initial={ngTime:new Date(1970, 0, 1, 19, 30, 0),ngDate:$scope.minDate};


    $scope.teams = ['team1', 'team2', 'team3'];
    $scope.team_ids=[1,2,3];

    // Selected teams
    $scope.teamSelection = [];
    $scope.teamSelection_ids=[];
    $scope.teamForms=[];

    // $scope.poolForm.ngDate = new Date();

    // Toggle selection for a given fruit by name
    $scope.toggleSelection = function toggleSelection(teamName) {
      var idx = $scope.teamSelection.indexOf(teamName);

      // Is currently selected
      if (idx > -1) {
        $scope.teamSelection.splice(idx, 1);
        $scope.teamSelection_ids.splice(idx,1);
      }

      // Is newly selected
      else {
        $scope.teamSelection.push(teamName);
        $scope.teamSelection_ids.push($scope.team_ids[$scope.teams.indexOf(teamName)]);
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
          $scope.resultText=response.data.message;
          $scope.teams=response.data.team_names;
          $scope.team_ids = response.data.team_ids;
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
    $log.log($scope.poolForm.ngDate);

    $scope.initial.ngTime.setDate($scope.initial.ngDate.getDate());
    var dateTime=$filter('date')($scope.initial.ngTime,'yy-MM-dd HH:mm');


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
        $scope.disabled = false;
        $log.log("Registration response::");
        $log.log(response.data);
        $scope.resultText=response.data;

      }).
      catch(function(response) {
        $scope.disabled = false;
        $scope.resultText="error registering pool.";
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
  ['$scope', '$location', 'AuthService','$route', '$routeParams','$log','$http',
  function ($scope, $location, AuthService,$route,$routeParams,$log,$http) {

    $scope.viewPool={};

    $scope.getPoolIds = function() {
      $log.log("Getting pool ids");
      $http.post('api/get_pool_ids')
        .then(function(response){
          $scope.pool_ids = response.data.ids;
          $scope.pool_names = response.data.names;
          $scope.pool_id_message = response.data.message;
       })
        .catch(function(response) {
          $log.log("Error in getPoolIds calling api/get_pool_ids API");
        });
    };

    $scope.getPoolInfo = function() {

      $log.log("Getting pool info");

      // get the number of generic participants from the input
      var pool_id = $scope.pool_id;
      // fire the API request
      $http.post('/view_pool/',{'pool_id':pool_id})
        .then(function(response) {
          $log.log("Logging pool info. Pool id:")
          $log.log(pool_id)
          $log.log(response.data);
          if (response.status==200){
            $scope.resultText="You are a member of this carpool!";
            $scope.viewPool=response.data;
          }
          else if (response.status==204){
            $scope.resultText="No such carpooling event.";
            $scope.viewPool={};
          }
          else if (response.status == 206){
            $scope.resultText="You are not a member of this carpool.";
            $scope.viewPool=response.data;
          }
          else {

          }

        }).
        catch(function(response) {
          $log.log(response.data);
          $scope.resultText="error"
        });
    };

  $scope.getPoolIds();

  if (!$routeParams.poolId){
    if ($scope.pool_ids && ($scope.pool_ids.length >0)){
      $scope.pool_id = $scope.pool_ids[0];
      $scope.getPoolInfo();
    }
  }
  else{
    $scope.pool_id = $routeParams.poolId;
    $scope.getPoolInfo();
  }

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


    $scope.teams = ['team1', 'team2', 'team3'];
    $scope.team_ids=[1,2,3];


    $scope.getTeams = function() {

      $log.log("Getting user's teams");

      // get the number of generic participants from the input

      // fire the API request
      // returns: {'team_names':team_names,'team_ids':team_ids,'message':message,}
      $http.post('/api/get_foreign_teams/')
        .then(function(response) {
          $log.log("Foreign Teams:");
          $log.log(response.data);
          $scope.resultText=response.data.message;
          $scope.foreignTeams=response.data.foreign_team_names;
          $scope.foreignTeam_ids = response.data.foreign_team_ids;
        }).
        catch(function(response) {
          $log.log(response.data);
          $scope.resultText="error obtaining teams.";
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




















// angular.module('myApp').controller('triggerController',
//   ['$scope', '$log','$http','$timeout','$location', 'AuthService',
//   function ('$scope', '$log','$http','$timeout','$location', 'AuthService') {

// $scope.sendSomeEmails = function() {
//       var pool_id = $scope.pool_id;
//       $http.post('/email_all/',{"pool_id":pool_id}).then(function(response) {
//           $log.log(response.data);
//           $scope.resultText="Successfuly sent all emails (js)" + String(response.data);
//         }).
//         catch(function(response) {
//           $log.log(response.data);
//         });
//     };
//     $scope.sendAllEmails = function() {
//       $http.post('/email_all/').
//         then(function(response) {
//           $log.log(response.data);
//           $scope.resultText="Successfuly sent all emails (js)" + String(response.data);
//         }).
//         catch(function(response) {
//           $log.log(response.data);
//         });
//     };
//     $scope.getResult = function() {

//       $log.log("Beginning Population");

//       // get the number of generic participants from the input
//       var userInput = $scope.n;
//       var randGen = $scope.randGen;
//       var numberPools = $scope.numberPools;

//       $log.log(randGen)
//       // fire the API request
//       $http.post('/q_populate/', {"n": userInput,"randGen":randGen,"numberPools":numberPools}).
//         then(function(response) {
//           $log.log(response.data);
//           getCarpoolerList(response.data);
//         }).
//         catch(function(response) {
//           $log.log(response.data);
//         });
//     };
//     function getCarpoolerList(jobID) {

//       var timeout = "";
//         var poller = function() {
//         // fire another request
//         $http.post('/results/',{'jobID':jobID}).
//           then(function(response) {
//             if(response.status === 202) {
//               $scope.resultText = "Trying hard to add to database (JS). " + response.data + " (Flask)."
//               $log.log(response.data, response.status);
//             } else if (response.status === 200){
//               $log.log(response.data);
//               var resultText = JSON.stringify(response.data);
//               $log.log(resultText);
//               $log.log(typeof response.data)
//               $scope.resultJSON=response.data;
//               $scope.resultText = "Successfully added carpoolers to database!";
//               // $scope.resultText = "FINISHED";
//               $timeout.cancel(timeout);
//               return false;
//             }
//             // continue to call the poller() function every 2 seconds
//             // until the timeout is cancelled
//             timeout = $timeout(poller, 2000);
//           })
//           .catch(function(response){
//             $scope.resultText = "Job failed! (JS). " + response.data + " (Flask)."
//               $log.log(response.data, response.status);
//           });
//       };
//       poller();
//     };


//     $scope.clearScope = function() {
//       $log.log("Clearing Scope")
//       $scope.resultText=undefined;
//       $scope.resultJSON=undefined;
//       $scope.viewPool=undefined;
//       $scope.haventStarted=undefined;
//       $scope.GT_JSON=undefined;
//     };

//      $scope.isNotEmpty = function(elementId) {
//       var lengthOfElement = document.getElementById(elementId).childNodes.length;
//       $log.log(document.getElementById(elementId))
//       $log.log("Length:")
//       $log.log(document.getElementById(elementId).childNodes.length)
//       if (lengthOfElement>0){
//         return true;
//       } else {
//         return false;
//       }
//     };

//     $scope.isString = function(what) {
//       // $log.log("Checking whether something is a string. Something:")
//       // $log.log(what)
//       var stringifiedVar = String(what);
//       // $log.log("Stringified version:")
//       // $log.log(stringifyifiedVar)
//       return stringifiedVar[0]==what[0];
//     };

//     $scope.hasChildren = function(bigL1) {
//             return angular.isArray(bigL1);
//     };

//     $scope.dropTabs = function() {

//       $log.log("Beginning dropTabs");

//       // get the number of generic participants from the input
//       var submission = $scope.submit;

//       // fire the API request
//       $http.post('/dropTabs').
//         then(function(response) {
//           $log.log(response.data);
//           $scope.resultText="Dropped table successfullly using angular! " + String(response.data) + "(server output)"

//           if(response.status === 302) {
//             $scope.resultText = "Please log in before sending this request (JS).";
//             $log.log(response.data, response.status);
//           } else if (response.status === 200){
//             $scope.resultText = "Successfully dropped tabs (JS). " + String(response.data) + " (FLASK)";
//             $log.log(response.data, response.status);
//           }
//         }).
//         catch(function(response) {
//           $log.log(response.data);

//           $scope.resultText="error in dropTabs (JS). " + String(response.data) + " (Python)."
//         });
//     };

//     $scope.getPoolInfo = function() {

//       $log.log("Getting pool info");

//       // get the number of generic participants from the input
//       var pool_id = $scope.pool_id;
//       // fire the API request
//       $http.post('/view_pool/',{'pool_id':pool_id}).then(function(response) {
//           $log.log("Logging pool info. Pool id:")
//           $log.log(pool_id)
//           $log.log(response.data);
//           $scope.resultText="Successfully queried for pool info!";
//           $scope.viewPool=response.data;
//         }).
//         catch(function(response) {
//           $log.log(response.data);
//           $scope.resultText="error"
//         });
//     };
//     $scope.repeatGroupThere = function() {
//       $log.log("Calling repeatGroupThere");
//       // fire the API request
//       $http.post('/q_repeat_groupthere/').
//         then(function(response) {
//           $log.log(response.data);
//           $log.log("For full results, visit: /GTresults/" + responts.data)
//           getGTList(response.data);
//         }).
//         catch(function(response) {
//           $log.log(response.data);
//         });
//     };
//     $scope.doGroupThere = function() {

//       $log.log("Calling GroupThere");

//       // get the number of generic participants from the input
//       var pool_id = $scope.pool_id
//       // fire the API request
//       $http.post('/q_groupthere/',{'pool_id':pool_id}).
//         then(function(response) {
//           $log.log(response.data);
//           $log.log("For full results, visit: /GTresults/" + response.data)
//           getGTList(responts.data);
//         }).
//         catch(function(response) {
//           $log.log(response.data);
//         });
//     };
//     function getGTList(jobID) {

//       var timeout = "";
//       var poller2 = function() {
//       // fire another request
//       $http.post('/GTresults/',{'jobID':jobID}).
//         then(function(response) {
//           if(response.status === 202) {
//             $scope.resultText = "Asking Flask for a response (JS). " + response.data + " (Flask).";
//             $log.log(response.data, response.status);
//           } else if (response.status === 200){
//             var resultText = JSON.stringify(response.data);
//             $log.log(resultText);
//             $scope.GT_JSON=response.data;
//             $scope.resultText = "Successfully did GroupThere!" + JSON.stringify(response.data.full);
//             // $scope.resultText = "FINISHED";
//             $timeout.cancel(timeout);
//             $log.log("For full results, visit: /GTresults/" + jobID)
//             return false;
//           }
//           // continue to call the poller() function every 2 seconds
//           // until the timeout is cancelled
//           timeout = $timeout(poller2, 2000);
//         });
//       };
//       poller2();
//     };

// }]);


