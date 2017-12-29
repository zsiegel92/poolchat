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
    for (var prefillKey in ['emtoken','teamusertoken','eventid']){
      if (prefillKey in r){
        $scope.prefillVals[prefillKey] = f(r[prefillKey]);
      }
    }


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
          $scope.disabled = false;
          if (response.status==200){
            alert("An email has been sent to " + $scope.registerFormValues.ngEmail + ". Please click the link to confirm your account and start using GroupThere.");
              $location.path('/login/' + String($scope.registerFormValues.ngEmail));
          } else if (response.status==201){
            var teamname = response.data.teamname;
            alert("Your account has been validated. You are ready to join events!");
            $location.path('/viewPool/');
          } else if (response.status>=202 && response.status<=203){
            //REDIRECT TO EVENT JOIN
            var teamname = response.data.teamname;
            if (response.status==203){
              var eventname = response.data.eventname;
              var go_to_pool_id = response.data.go_to_pool_id;
              alert("Your account has been validated. You are ready to join events with team " + teamname + "! In particular, you have been invited to join event " + eventname + ".");
              $location.path('/viewPool/join_pool/'+response.data.go_to_pool_id);
            }
            else {
              alert("Your account has been validated. You are ready to join events with team " + teamname + "!");
              // response.data in this case contains pool id. see api_register
              $location.path('/viewPool/';
            }
          }
          else{
            $scope.registerFormValues.ngPassword='';
            $scope.registerFormValues.ngConfirm_password='';
            $scope.registerFormValues.ngAccept_tos =false;
            $scope.errorMessage=response.data;
          }
        })
        // handle error
        .catch(function (response) {
          $scope.error = true;
          $scope.errorMessage = response.data;
          $scope.disabled = false;
          $scope.registerFormValues.ngPassword='';
          $scope.registerFormValues.ngConfirm_password='';
          $scope.registerFormValues.ngAccept_tos =false;
          $scope.errorMessage=response.data;
        });

    };

}]);
