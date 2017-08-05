(function () {

  'use strict';

  angular.module('TriggerPane', [])



	.controller('TriggerController', ['$scope', '$log', '$http', '$timeout',
	  function($scope, $log, $http, $timeout) {

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

	  $scope.clearScope = function() {
	  	$scope.resultText=undefined;
	  	$scope.resultJSON=undefined;
	  	$scope.output_list=undefined;
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
		  // var poller = function() {
		  //   // fire another request
		  //   $http.get('/results/'+jobID).
		  //     success(function(data, status, headers, config) {
		  //       if(status === 202) {
		  //       	$scope.resultText = "Trying hard to add to database (JS). " + data + " (Flask)."
		  //         $log.log(data, status);
		  //       } else if (status === 200){
		  //         // $log.log(data);
		  //         var resultText = new String(data);
		  //         $scope.resultJSON=data
		  //         $scope.resultText = resultText;
		  //         // $scope.resultText = "FINISHED";
		  //         $timeout.cancel(timeout);
		  //         return false;
		  //       }
		  //       // continue to call the poller() function every 2 seconds
		  //       // until the timeout is cancelled
		  //       timeout = $timeout(poller, 2000);
		  //     });
		  // };
		  poller();
		}
	}
	]);
}());



