'use strict'

angular.module('myApp.register', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider
    .when('/register/:email?/:emtoken?/:teamusertoken?/:eventid?/:firstname?/:lastname?', {
      templateUrl: 'static/register/register.html',
      controller: 'registerController',
      access: {restricted: false}
    });
}])
.controller('registerController',
  ['$scope', '$location', '$log','AuthService','$window','$routeParams',
  function ($scope, $location,$log, AuthService,$window,$routeParams) {
    var f = $window.decodeURIComponent;
    var r = $routeParams;
    $scope.registerFormValues ={};

    var routeFormKeys= {"email" : "ngEmail","firstname" : "ngFirst","lastname" : "ngLast"};
    for (var routeKey in routeFormKeys){
      if (routeKey in r){
        $scope.registerFormValues[routeFormKeys[routeKey]] = f(r[routeKey]);
      }
    }


    $scope.prefillVals = {};
    ['emtoken','teamusertoken','eventid'].forEach(function(prefillKey, index) {
      if (prefillKey in r){
        $scope.prefillVals[prefillKey] = r[prefillKey]; //raw! Do not decode keys!
      }
    });



    $scope.register = function () {

      // initial values
      $scope.error = false;
      $scope.disabled = true;
      // $log.log([$scope.registerForm.ngFirst,$scope.registerForm.ngLast,$scope.registerForm.ngEmail,$scope.registerForm.ngPassword,$scope.registerForm.ngConfirm_password,$scope.registerForm.ngAccept_tos]);

      // call register from service
      // response is raw response from /api/register
      AuthService.register($scope.registerFormValues.ngFirst,$scope.registerFormValues.ngLast,$scope.registerFormValues.ngEmail,$scope.registerFormValues.ngPassword,$scope.registerFormValues.ngConfirm_password,$scope.registerFormValues.ngAccept_tos,$scope.prefillVals)
        // handle success
        .then(function (response) {
          var status = response.data.status;
          $scope.disabled = false;
          if (status==200){
            alert("An email has been sent to " + $scope.registerFormValues.ngEmail + ". Please click the link to confirm your account and start using GroupThere.");
              $location.path('/login/' + String($scope.registerFormValues.ngEmail));
          } else if (status==201){
            var teamname = response.data.teamname;
            alert("Your account has been validated. You are ready to join events!");
            $location.path('/viewPool/');
          } else if (status>=202 && status<=203){
            //REDIRECT TO EVENT JOIN
            var teamname = response.data.teamname;
            if (status==203){
              var eventname = response.data.eventname;
              var go_to_pool_id = response.data.go_to_pool_id;
              alert("Your account has been validated. You are ready to join events with team " + teamname + "! In particular, you have been invited to join event " + eventname + ".");
              $location.path('/viewPool/join_pool/'+response.data.go_to_pool_id);
            } else {
              alert("Your account has been validated. You are ready to join events with team " + teamname + "!");
              // response.data in this case contains pool id. see api_register
              $location.path('/viewPool/');
            }
          } else if (status>=204 && status<=205){
              var teamname = response.data.teamname;
              if (status==205){
                var eventname = response.data.eventname;
                var go_to_pool_id = response.data.go_to_pool_id;
                alert("You already have an account! You are ready to join events with team " + teamname + "! In particular, you have been invited to join event " + eventname + ".");
                $location.path('/viewPool/join_pool/'+response.data.go_to_pool_id);
              } else {
                alert("Your already have an account! You are now ready to join events with team " + teamname + "!");
                $location.path('/viewPool/');
            }
          } else{
            $scope.error = true;
            $scope.disabled = false;
            $scope.registerFormValues.ngPassword='';
            $scope.registerFormValues.ngConfirm_password='';
            $scope.registerFormValues.ngAccept_tos =false;
            // $scope.errorMessage=response.data;
            // $scope.errorMessage="Something went wrong with registration. It's possible that this email address is already in use. Try <a href='/#!/login'>logging in</a>, or <a href='/#!/forgotPassword'>password recovery</a>.";
          }
        })
        // handle error
        .catch(function (response) {
          $scope.error = true;
          $scope.disabled = false;
          $scope.registerFormValues.ngPassword='';
          $scope.registerFormValues.ngConfirm_password='';
          $scope.registerFormValues.ngAccept_tos =false;
          // $scope.errorMessage=response.data;
          // $scope.errorMessage="Something went wrong with registration. It's possible that this email address is already in use. Try <a href='/#!/login'>logging in</a>, or <a href='/#!/forgotPassword'>password recovery</a>.";
        });

    };

    // AuthService.requestMyEmail();
    // var logged_in_email = AuthService.getMyEmail();
    // if (('email' in r) && (logged_in_email.toUpperCase()===f(r.email).toUpperCase())){
    //   $scope.error = false;
    //   $scope.disabled = true;

    //   AuthService.register('xxxxx','xxxxx',$scope.registerFormValues.ngEmail,'xxxxx','xxxxx',true,$scope.prefillVals)
    //     // handle success
    //     .then(function (response) {});
    // }



    AuthService.requestMyEmail().then(function(){
      var logged_in_email = AuthService.getMyEmail();
      if (('email' in r) && (typeof logged_in_email === 'string' || logged_in_email instanceof String) && (typeof f(r.email) === 'string' || f(r.email) instanceof String) && (logged_in_email.toUpperCase()===f(r.email).toUpperCase())){
        $log.log("GOT THIS FAR");
        $scope.error = false;
        $scope.disabled = true;
        AuthService.register('xxxxx','xxxxx',$scope.registerFormValues.ngEmail,'xxxxx','xxxxx',true,$scope.prefillVals)
          // handle success
          .then(function(response) {
            $log.log("LOGGING RESPONSE.DATA");
            $log.log(response.data);
            var status = response.data.status;
            if (status>=204 && status<=205){
            var teamname = response.data.teamname;
            if (status==205){
              var eventname = response.data.eventname;
              var go_to_pool_id = response.data.go_to_pool_id;
              alert("You already have an account! You are ready to join events with team " + teamname + "! In particular, you have been invited to join event " + eventname + ".");
              $location.path('/viewPool/join_pool/'+response.data.go_to_pool_id);
            } else {
              alert("Your already have an account! You are now ready to join events with team " + teamname + "!");
              $location.path('/viewPool/');
            }
          }else{
            $log.log("ERROR in register.js, response bad from AuthService.register on oneclick attempt.");
            // $log.log(response);
            $scope.error = true;
            $scope.errorMessage="You have attempted to use a 1-click registration link, but there was an error. Make sure no user is logged in on this device, and make sure you don't already have an account.";
          }
          })
          .catch(function(response){
            $log.log("ERROR in register.js, response bad from AuthService.register on oneclick attempt.");
            // $log.log(response);
            $scope.error = true;
            $scope.errorMessage="You have attempted to use a 1-click registration link, but there was an error. Make sure no user is logged in on this device, and make sure you don't already have an account.";
          });
      }
    $scope.disabled = false;
    });




}]);
