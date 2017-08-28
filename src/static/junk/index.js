(function () {

  'use strict';

  angular.module('IndexPane', [])
	  .config(['$httpProvider', function($httpProvider) {
	  $httpProvider.defaults.withCredentials = true;
		}])

		.factory('AuthService',
		  ['$q', '$timeout', '$http',
		  function ($q, $timeout, $http) {

		    // create user variable
		    var user = null;

		    // return available functions for use in controllers
		    return ({
		      isLoggedIn: isLoggedIn,
		      login: login,
		      logout: logout,
		      register: register
		    });

			}])

		.controller('IndexController', ['$scope', '$log', '$http', '$timeout',
		  function($scope, $log, $http, $timeout) {


		  $scope.clearScope = function() {
		  	$log.log("Clearing Scope")
		  };

		   $scope.isNotEmpty = function(elementId) {
		   	var lengthOfElement = document.getElementById(elementId).childNodes.length;
		   	$log.log(document.getElementById(elementId))
		   	$log.log("Length:")
		   	$log.log(document.getElementById(elementId).childNodes.length)
		   	if (lengthOfElement>0){
		   		return true;
		   	} else {
		   		return false;
		   	}
		  };
			$scope.isString = function(what) {
				// $log.log("Checking whether something is a string. Something:")
				// $log.log(what)
				var stringifiedVar = String(what);
				// $log.log("Stringified version:")
				// $log.log(stringifyifiedVar)
	    	return stringifiedVar[0]==what[0];
			};
			$scope.hasChildren = function(bigL1) {
	            return angular.isArray(bigL1);
			};



		  $scope.getCarpoolerInfo = function() {

		    $log.log("Getting carpooler info");

		    // get the carpooler email from form
		    var carpooler_email = $scope.emailField;
		    // var formdata = new FormData()
		    // formdata.append('emailField',carpooler_email)
		    var formdata = {'emailField':carpooler_email};
		    // $httpParamSerializerJQLike
		  //   $log.log("Logging form data:")
				// $log.log(formdata);

				// $http.post('/view_carpooler/',form,{'params':{'mimeType':'multipart/form-data'}})
		    $http({
				  method  : 'POST',
				  url     : '/view_carpooler/',
				  data    : $.param(formdata),  //$httpParamSerializerJQLike(formdata)// pass in data as strings
				  headers : { 'Content-Type': 'application/x-www-form-urlencoded' }
				 }).then(function(response) {
							$log.log("Queried carpooler info. Response data:");
		        	$log.log(response.data);

						if(response.status === 200) {
		        	$scope.resultText="Welcome back!";
		       		$scope.viewPooler= response.data;

		        } else if (response.status === 201){
			        $scope.resultText="Welcome to GroupThere! You have been added to our database.";
			        $scope.viewPooler= response.data;

		        } else if (response.status === 500){
			        $scope.resultText="Something was wrong with your input." + String(response.data);
			        // $scope.viewPooler= String(response.data);
			        }

		      }).
		      catch(function(response) {
		        $log.log(response.data);
		        $scope.resultText="Something was wrong with your input." + String(response.data)
		      });
		  };

		  $scope.doGroupThere = function() {

		    $log.log("Calling GroupThere");

		    // get the number of generic participants from the input
		    var pool_id = $scope.pool_id
		    // fire the API request
		    $http.post('/q_groupthere/',{'pool_id':pool_id}).
		      then(function(response) {
		        $log.log(response.data);
		        $log.log("For full results, visit: /GTresults/" + response.data)
		        getGTList(responts.data);
		      }).
		      catch(function(response) {
		        $log.log(response.data);
		      });
		  };
			function getGTList(jobID) {

			  var timeout = "";
		 		var poller2 = function() {
		    // fire another request
		    $http.post('/GTresults/',{'jobID':jobID}).
		      then(function(response) {
		        if(response.status === 202) {
		        	$scope.resultText = "Asking Flask for a response (JS). " + response.data + " (Flask).";
		          $log.log(response.data, response.status);
		        } else if (response.status === 200){
		          var resultText = JSON.stringify(response.data);
		          $log.log(resultText);
		          $scope.GT_JSON=response.data;
		          $scope.resultText = "Successfully did GroupThere!" + JSON.stringify(response.data.full);
		          // $scope.resultText = "FINISHED";
		          $timeout.cancel(timeout);
		          $log.log("For full results, visit: /GTresults/" + jobID)
		          return false;
		        }
		        // continue to call the poller() function every 2 seconds
		        // until the timeout is cancelled
		        timeout = $timeout(poller2, 2000);
		      });
			  };
			  poller2();
			};





		}
		]);
}());



