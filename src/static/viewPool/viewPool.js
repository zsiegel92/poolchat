'use strict'

angular.module('myApp.viewPool', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider
    .when('/viewPool', {
      templateUrl: 'static/viewPool/viewPool.html',
      controller: 'viewPoolController',
      access: {restricted: true}
    })
    .when('/viewPool/join_pool/:go_to_pool_id?', {
      templateUrl: 'static/viewPool/viewPool.html',
      controller: 'viewPoolController',
      access: {restricted: true}
    });
}])
.controller('viewPoolController',
  ['$scope', '$location', 'AuthService','$route', '$routeParams','$log','$http','$window','$timeout','$filter',
  function ($scope, $location, AuthService,$route,$routeParams,$log,$http,$window,$timeout,$filter) {


    var hours=0;
    var minutes = 0;
    var seconds=0;
    $scope.toDays = function(secs){
      return Math.floor(secs/86400);
    };
    $scope.toHours = function(secs){
      return Math.floor(secs/3600) % 24;
    };
    $scope.toMinutes = function(secs){
      return Math.floor(secs/60) % 60;
    };
    $scope.toSeconds = function(secs){
      return Math.floor(secs)%60;
    };



    $scope.counter = 0;
    $scope.onTimeout = function(){
        $scope.counter++;
        mytimeout = $timeout($scope.onTimeout,1000);
    };
    var mytimeout = $timeout($scope.onTimeout,1000);
    // $scope.stop = function(){
    //     $timeout.cancel(mytimeout);
    // };

    $scope.past_addresses=[];



      // call after $scope.eligible_pools is defined
      var f = $window.decodeURIComponent;
      var r = $routeParams;
      var go_to_pool_id = f(r.go_to_pool_id);





    $scope.getPoolInfoForUser = function() {
      $log.log("Getting pool info");
      $http.post('api/get_pool_info_for_user')
        .then(function(response){
          $scope.teams = response.data.teams;
          $scope.joined_pools = response.data.joined_pools;
          $scope.eligible_pools = response.data.eligible_pools;
          $scope.carpooler = response.data.carpooler;
          $scope.rawResponse= response.data;
          if ($scope.eligible_pools.length >0){
            $log.log("There is an eligible pool!");
            // $scope.joinForm.ngPool=0; //Prevents form from being invalid due to 'required', but fails to actually select a pool on menu.
          }
          else{
            $log.log("There are no eligible pools!");
          }
          var ad = '';
          $scope.max_num_seats =0;
          $scope.ever_must_drive=0;
          $scope.ever_organizer=0;
          var pool;
          for (var i = 0; i < $scope.joined_pools.length; i++) {
            pool = $scope.joined_pools[i];
            ad = pool.trip.address;
            if (ad){
              if ($scope.past_addresses.indexOf(ad) == -1 && ad !=''){
                $scope.past_addresses.push(pool.trip.address);
              }
            }
            if (pool.trip.num_seats && pool.trip.num_seats > $scope.max_num_seats){
                $scope.max_num_seats = $scope.joined_pools[i].trip.num_seats;
            }
            if (!$scope.ever_organizer && pool.trip.on_time && pool.trip.on_time==1){
              $scope.ever_organizer=1;
            }
           if (!$scope.ever_must_drive && pool.trip.must_drive && pool.trip.must_drive==1){
              $scope.ever_must_drive=1;
            }
          }

          var now = new Date();
          for (let pool1 of $scope.eligible_pools) {
            pool1.seconds_til = Math.floor((new Date(Date.parse(pool1.dateTime)).getTime() - now.getTime())/1000);
            pool1.seconds_til_instructions = Math.floor((new Date(Date.parse(pool1.dateTime)).getTime() - pool1.fireNotice*60*60*1000 - now.getTime())/1000);
            // new Date(Date.parse(pool.dateTime)).getTime()
            // (pool.dateTime.getTime() - now.getTime())/1000;
          }
          for (let pool2 of $scope.joined_pools) {
            pool2.seconds_til = Math.floor((new Date(Date.parse(pool2.dateTime)).getTime() - now.getTime())/1000);
            pool2.seconds_til_instructions = Math.floor((new Date(Date.parse(pool2.dateTime)).getTime() - pool2.fireNotice*60*60*1000 - now.getTime())/1000);
            // new Date(Date.parse(pool.dateTime)).getTime()
            // (pool.dateTime.getTime() - now.getTime())/1000;
          }


          $log.log("Successfully queried for teams, joined_pools, and eligible_pools!");
          $log.log(response.data);

          if (go_to_pool_id){
            $log.log("Checking whether re-route requested.")
            for (var i = 0; i < $scope.eligible_pools.length; i++) {
              if ($scope.eligible_pools[i].id == go_to_pool_id){
                $scope.joinForm.ngPool=i;
                $scope.goto_join();
              }
            }
          }
       })
        .catch(function(response) {
          $scope.errorText=response.data;
          $log.log("Error in getPoolInfo calling api/get_pool_info API");
        });
    };


    $scope.asDateTime = function(dateStr) {
      return new Date(Date.parse(dateStr));
    };



    $scope.modalShown = false;
    $scope.toggleModal = function() {
      $scope.modalShown = !$scope.modalShown;
    };

    $scope.getPoolInfoForUser();

    $scope.getPoolInstructions = function(ind) {
      $scope.disabled=true;
      $scope.waiting_for_instructions_text="Fetching instructions. Please wait.";
      var pool = $scope.joined_pools[ind];
      $scope.instruction_pool =$scope.joined_pools[ind];
      $scope.current_instruction=ind;
      $http.post('/api/get_most_recent_instructions',
                  $.param(
                    {
                      pool_id:pool.id
                    }
                  ),
                  {headers: {'Content-Type': 'application/x-www-form-urlencoded'}})

          .then(function(response) {
            $scope.disabled = false;
            $scope.waiting_for_instructions_error=undefined;
            $scope.waiting_for_instructions_text=undefined;
            $log.log("Getting instruction information");
            $log.log(response.data);
            $scope.instruction = response.data;
            if ($scope.instruction.my_ass_index > -1){
              $scope.myAssignment = $scope.instruction.assignments[$scope.instruction.my_ass_index];
              $scope.instruction.assignments.splice($scope.instruction.my_ass_index,1);
            }
            $log.log("My assignment:");
            $log.log($scope.myAssignment);
            $log.log("Other assignments:");
            $log.log($scope.instruction.assignments);
            $scope.errorText=undefined;
            $scope.toggleModal();
          }).
          catch(function(response) {
            $scope.waiting_for_instructions_text=undefined;
            $scope.waiting_for_instructions_error="Error obtaining instructions. Please try again.";
            $scope.disabled = false;
            $scope.errorText=response.data;
          });
    };
    $scope.redoPool = function(ind) {
      var pool = $scope.joined_pools[ind];

      $http.post('/api/re_optimize',
                  $.param(
                    {
                      pool_id:pool.id
                    }
                  ),
                  {headers: {'Content-Type': 'application/x-www-form-urlencoded'}})

          .then(function(response) {
            $scope.disabled = false;
            $log.log("Re-Optimizing");
            $scope.resultText=response.data;
            $scope.errorText=undefined;
          }).
          catch(function(response) {
            $scope.disabled = false;
            $scope.errorText=response.data;
          });
    };


    //route: '/joinPool/:id/name/:name/address/:address/date/:date/time/:time/email/:email/notice/:notice/latenessWindow/:latenessWindow'
    $scope.goto_join = function(joined_index=-1){
      var f= $window.encodeURIComponent;
      var cp = $scope.carpooler;

      if (joined_index > -1){
        $log.log("Re-submitting trip information.");
        var pool = $scope.joined_pools[joined_index];
        var repeat = true;
        var pth = '/joinPool/' + f(pool.id) +'/name/'+ f(pool.name) + '/address/' + f(pool.address) + '/date/' + f(pool.date) + '/time/' + f(pool.time) + '/dateTime/' + f(pool.dateTime) + '/email/' + f(pool.email) + '/notice/' + f(pool.fireNotice) + "/latenessWindow/" + f(pool.latenessWindow) +"/carpooler/cpname/" + f(cp.name) + '/cpfirst/' + f(cp.first) + '/cplast/' + f(cp.last) + '/cpemail/' + f(cp.email) + '/past_addresses/' + f(JSON.stringify($scope.past_addresses)) + '/max_seats/' + f($scope.max_num_seats) + '/ever_must_drive/' + f($scope.ever_must_drive) + '/ever_organizer/' + f($scope.ever_organizer) + '/' + f(repeat) + '/' + f(pool.trip.address) + '/' + f(pool.trip.num_seats) + '/' + f(pool.trip.preWindow) + '/' + f(pool.trip.on_time) + '/' + f(pool.trip.must_drive);
      }
      else{
        $log.log("Joining a new pool!");
        var pool = $scope.eligible_pools[$scope.joinForm.ngPool];
        var repeat = false;
        var pth = '/joinPool/' + f(pool.id) +'/name/'+ f(pool.name) + '/address/' + f(pool.address) + '/date/' + f(pool.date) + '/time/' + f(pool.time) + '/dateTime/' + f(pool.dateTime) + '/email/' + f(pool.email) + '/notice/' + f(pool.fireNotice) + "/latenessWindow/" + f(pool.latenessWindow) +"/carpooler/cpname/" + f(cp.name) + '/cpfirst/' + f(cp.first) + '/cplast/' + f(cp.last) + '/cpemail/' + f(cp.email) + '/past_addresses/' + f(JSON.stringify($scope.past_addresses)) + '/max_seats/' + f($scope.max_num_seats) + '/ever_must_drive/' + f($scope.ever_must_drive) + '/ever_organizer/' + f($scope.ever_organizer) + '/' + f(repeat);
      }


      $log.log(pth);
      // $log.log($window.encodeURIComponent(pth));
      // $location.path($window.encodeURIComponent(pth));
      $location.path(pth);
  };


}]);
