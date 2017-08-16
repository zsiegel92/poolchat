(function () {

  'use strict';

  angular.module('TriggerPane', [])

  .config(['$httpProvider', function($httpProvider) {
  $httpProvider.defaults.withCredentials = true;
	}])

	.controller('TriggerController', ['$scope', '$log', '$http', '$timeout',
	  function($scope, $log, $http, $timeout) {

	  $scope.sendSomeEmails = function() {
	  	var pool_id = $scope.pool_id;
	  	$http.post('/email_all/',{"pool_id":pool_id}).then(function(response) {
	        $log.log(response.data);
					$scope.resultText="Successfuly sent all emails (js)" + String(response.data);
	      }).
	      catch(function(response) {
	        $log.log(response.data);
	      });
	  };
	  $scope.sendAllEmails = function() {
	  	$http.post('/email_all/').
	      then(function(response) {
	        $log.log(response.data);
					$scope.resultText="Successfuly sent all emails (js)" + String(response.data);
	      }).
	      catch(function(response) {
	        $log.log(response.data);
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
	      then(function(response) {
	        $log.log(response.data);
	        getCarpoolerList(response.data);
	      }).
	      catch(function(response) {
	        $log.log(response.data);
	      });
	  };
		function getCarpoolerList(jobID) {

		  var timeout = "";
		 		var poller = function() {
		    // fire another request
		    $http.post('/results/',{'jobID':jobID}).
		      then(function(response) {
		        if(response.status === 202) {
		        	$scope.resultText = "Trying hard to add to database (JS). " + response.data + " (Flask)."
		          $log.log(response.data, response.status);
		        } else if (response.status === 200){
		          $log.log(response.data);
		          var resultText = JSON.stringify(response.data);
		          $log.log(resultText);
		          $log.log(typeof response.data)
		          $scope.resultJSON=response.data;
		          $scope.resultText = "Successfully added carpoolers to database!";
		          // $scope.resultText = "FINISHED";
		          $timeout.cancel(timeout);
		          return false;
		        }
		        // continue to call the poller() function every 2 seconds
		        // until the timeout is cancelled
		        timeout = $timeout(poller, 2000);
		      })
		      .catch(function(response){
		      	$scope.resultText = "Job failed! (JS). " + response.data + " (Flask)."
		          $log.log(response.data, response.status);
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
	    $http.post('/dropTabs').
	      then(function(response) {
	        $log.log(response.data);
	        $scope.resultText="Dropped table successfullly using angular! " + String(response.data) + "(server output)"

					if(response.status === 302) {
	        	$scope.resultText = "Please log in before sending this request (JS).";
	          $log.log(response.data, response.status);
	        } else if (response.status === 200){
	         	$scope.resultText = "Successfully dropped tabs (JS). " + String(response.data) + " (FLASK)";
	          $log.log(response.data, response.status);
	        }









	      }).
	      catch(function(response) {
	        $log.log(response.data);

	        $scope.resultText="error in dropTabs (JS). " + String(response.data) + " (Python)."
	      });
	  };

	  $scope.getPoolInfo = function() {

	    $log.log("Getting pool info");

	    // get the number of generic participants from the input
	    var pool_id = $scope.pool_id;
	    // fire the API request
	    $http.post('/view_pool/',{'pool_id':pool_id}).then(function(response) {
	      	$log.log("Logging pool info. Pool id:")
	      	$log.log(pool_id)
	        $log.log(response.data);
	        $scope.resultText="Successfully queried for pool info!";
	        $scope.viewPool=response.data;
	      }).
	      catch(function(response) {
	        $log.log(response.data);
	        $scope.resultText="error"
	      });
	  };
	  $scope.repeatGroupThere = function() {
	  	$log.log("Calling repeatGroupThere");
	    // fire the API request
	    $http.post('/q_repeat_groupthere/').
	      then(function(response) {
	        $log.log(response.data);
	        $log.log("For full results, visit: /GTresults/" + responts.data)
	        getGTList(response.data);
	      }).
	      catch(function(response) {
	        $log.log(response.data);
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



