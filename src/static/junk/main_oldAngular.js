(function () {

  'use strict';

  angular.module('TriggerPane', [])



	.controller('TriggerController', ['$scope', '$log', '$http', '$timeout',
	  function($scope, $log, $http, $timeout) {

	  $scope.sendSomeEmails = function() {
	  	var pool_id = $scope.pool_id;
	  	$http.post('/email_all/',{"pool_id":pool_id}).
	      success(function(results) {
	        $log.log(results);
					$scope.resultText="Successfuly sent all emails (js)" + String(results);
	      }).
	      error(function(error) {
	        $log.log(error);
	      });
	  };
	  $scope.sendAllEmails = function() {
	  	$http.post('/email_all/').
	      success(function(results) {
	        $log.log(results);
					$scope.resultText="Successfuly sent all emails (js)" + String(results);
	      }).
	      error(function(error) {
	        $log.log(error);
	      });
	  };
	  $scope.getResult = function() {

	    $log.log("Beginning Population");

	    // get the number of generic participants from the input
	    var userInput = $scope.n;
	    var randGen = $scope.randGen;
	    var numberPools = $scope.numberPools;

	    $log.log(randGen)
	    // fire the API request
	    $http.post('/q_populate/', {"n": userInput,"randGen":randGen,"numberPools":numberPools}).
	      success(function(results) {
	        $log.log(results);
	        getCarpoolerList(results);
	      }).
	      error(function(error) {
	        $log.log(error);
	      });
	  };
		function getCarpoolerList(jobID) {

		  var timeout = "";
		 		var poller = function() {
		    // fire another request
		    $http.post('/results/',{'jobID':jobID}).
		      success(function(data, status, headers, config) {
		        if(status === 202) {
		        	$scope.resultText = "Trying hard to add to database (JS). " + data + " (Flask)."
		          $log.log(data, status);
		          $log.log("SOME JS SHIT");
		        } else if (status === 200){
		          $log.log(data);
		          var resultText = JSON.stringify(data);
		          $log.log(resultText);
		          $log.log(typeof data)
		          $scope.resultJSON=data;
		          $scope.resultText = "Successfully added carpoolers to database!";
		          // $scope.resultText = "FINISHED";
		          $timeout.cancel(timeout);
		          return false;
		        }
		        // continue to call the poller() function every 2 seconds
		        // until the timeout is cancelled
		        timeout = $timeout(poller, 2000);
		      });
		  };
		  poller();
		};


	  $scope.clearScope = function() {
	  	$log.log("Clearing Scope")
	  	$scope.resultText=undefined;
	  	$scope.resultJSON=undefined;
	  	$scope.output_list=undefined;
	  	$scope.viewPool=undefined;
	  	$scope.haventStarted=undefined;
	  	$scope.GT_JSON=undefined;
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

	  $scope.dropTabs = function() {

	    $log.log("Beginning dropTabs");

	    // get the number of generic participants from the input
	    var submission = $scope.submit;

	    // fire the API request
	    $http.get('/dropTabs').
	      success(function(data, status, headers, config) {
	        $log.log(data);
	        $scope.resultText="Dropped table successfullly using angular!"
	      }).
	      error(function(error) {
	        $log.log(error);
	        $scope.resultText="error"
	      });
	  };

	  $scope.getPoolInfo = function() {

	    $log.log("Getting pool info");

	    // get the number of generic participants from the input
	    var pool_id = $scope.pool_id;
	    // fire the API request
	    $http.post('/view_pool/',{'pool_id':pool_id}).
	      success(function(data, status, headers, config) {
	      	$log.log("Logging pool info. Pool id:")
	      	$log.log(pool_id)
	        $log.log(data);
	        $scope.resultText="Successfully queried for pool info!";
	        $scope.viewPool=data;
	      }).
	      error(function(error) {
	        $log.log(error);
	        $scope.resultText="error"
	      });
	  };
	  $scope.repeatGroupThere = function() {
	  	$log.log("Calling repeatGroupThere");
	    // fire the API request
	    $http.post('/q_repeat_groupthere/').
	      success(function(results) {
	        $log.log(results);
	        $log.log("For full results, visit: /GTresults/" + results)
	        getGTList(results);
	      }).
	      error(function(error) {
	        $log.log(error);
	      });
	  };
	  $scope.doGroupThere = function() {

	    $log.log("Calling GroupThere");

	    // get the number of generic participants from the input
	    var pool_id = $scope.pool_id
	    // fire the API request
	    $http.post('/q_groupthere/',{'pool_id':pool_id}).
	      success(function(results) {
	        $log.log(results);
	        $log.log("For full results, visit: /GTresults/" + results)
	        getGTList(results);
	      }).
	      error(function(error) {
	        $log.log(error);
	      });
	  };
		function getGTList(jobID) {

		  var timeout = "";
		 		var poller2 = function() {
		    // fire another request
		    $http.post('/GTresults/',{'jobID':jobID}).
		      success(function(data, status, headers, config) {
		        if(status === 202) {
		        	$scope.resultText = "Asking Flask for a response (JS). " + data + " (Flask).";
		          $log.log(data, status);
		        } else if (status === 200){
		          var resultText = JSON.stringify(data);
		          $log.log(resultText);
		          $scope.GT_JSON=data;
		          $scope.resultText = "Successfully did GroupThere!" + JSON.stringify(data.full);
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



