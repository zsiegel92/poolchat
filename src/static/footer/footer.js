'use strict'

angular.module('myApp.footer', ['ngRoute'])

.controller('footController',
  ['$scope', '$location', '$http','AuthService','$rootScope','$log',
  function ($scope, $location, $http, AuthService,$rootScope,$log) {

    $scope.disabled=false;
    $scope.contactFormValues ={textValue:'',emailValue:''};

    $log.log("Starting up footController");


    $scope.send_feedback_email = function() {
      if ($scope.contactForm.$invalid){
        $log.log("Please enter a valid email and message");
      }
      else{
        $scope.disabled=true;

        $http.post('api/report_feedback',
              $.param(
                {
                  email:$scope.contactFormValues.emailValue,
                  feedback_message:$scope.contactFormValues.textValue
                }
              ),
              {headers: {'Content-Type': 'application/x-www-form-urlencoded'}})
          .then(function(response) {
            $scope.disabled = false;
            $scope.contactFormValues.textValue='';
            $scope.contactForm.$setPristine();
            alert("Thanks for your feedback!");
          }).
          catch(function(response) {
            $scope.disabled = false;
            alert("Something went wrong! Your feedback was not submitted.");
          });
        $log.log("Sending email!");
      }
    };

}]);

