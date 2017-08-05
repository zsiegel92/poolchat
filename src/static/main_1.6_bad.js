(function () {

  'use strict';

  angular.module('TriggerPane', [])



	.controller('TriggerController', ['$scope', '$log', '$http', '$timeout',
	  function($scope, $log, $http, $timeout) {

	  $scope.getResult = function() {

	    $log.log("Beginning Population");

	    // get the number of generic participants from the input
	    var userInput = $scope.n;

	    // fire the API request
	    $http.post('/q_populate/', {"n": userInput}).
	      then(successCallback(response) {
	        $log.log(response.data);
	        getCarpoolerList(response.data);
	      },
	      function errorCallback(response){
	        $log.log(response.statusText);
	      });
	  };
		function getCarpoolerList(jobID) {

		  var timeout = "";

		  var poller = function() {
		    // fire another request
		    $http.get('/results/'+jobID).
		      then(function(response) {
		        if(response.status === 202) {
		        	$scope.resultText = "Trying hard to add to database (JS). " + response.data + " (Flask)."
		          $log.log(response.data, response.status);
		        } else if (response.status === 200){
		          // $log.log(data);
		          var resultText = new String(response.data);
		          $scope.resultText = resultText;
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
		}
	}
	]);
}());

