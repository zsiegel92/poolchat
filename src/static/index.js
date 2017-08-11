(function () {

  'use strict';

  angular.module('IndexPane', [])



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

	    // fire the API request
	    $http.post('/view_carpooler/',{'email':carpooler_email}).then(function(response) {
	      	$log.log("Logging carpooler info. Carpooler email:");
	      	$log.log(carpooler_email);
	        $log.log(response.data);
	        $scope.resultText="Successfully queried for carpooler info! (JS)";
	        $scope.viewPooler= String(response.data);
	      }).
	      catch(function(response) {
	        $log.log(response.data);
	        $scope.resultText="error"
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



