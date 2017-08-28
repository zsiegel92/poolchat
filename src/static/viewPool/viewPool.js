'use strict'

angular.module('myApp.viewPool', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider
    .when('/viewPool', {
      templateUrl: 'static/viewPool/viewPool.html',
      controller: 'viewPoolController',
      access: {restricted: true}
    });
}])
.controller('viewPoolController',
  ['$scope', '$location', 'AuthService','$route', '$routeParams','$log','$http','$window',
  function ($scope, $location, AuthService,$route,$routeParams,$log,$http,$window) {

    $scope.past_addresses=[];

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
          for (var i = 0; i < $scope.joined_pools.length; i++) {
            var pool = $scope.joined_pools[i];
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


          $log.log("Successfully queried for teams, joined_pools, and eligible_pools!");
          $log.log(response.data);
       })
        .catch(function(response) {
          $log.log("Error in getPoolInfo calling api/get_pool_info API");
        });
    };


    $scope.asDateTime = function(dateStr) {
      return new Date(Date.parse(dateStr));
    };

  $scope.getPoolInfoForUser();

  //route: '/joinPool/:id/name/:name/address/:address/date/:date/time/:time/email/:email/notice/:notice/latenessWindow/:latenessWindow'
  $scope.goto_join = function(){
    var pool = $scope.eligible_pools[$scope.joinForm.ngPool];
    var cp = $scope.carpooler;

    var f= $window.encodeURIComponent;
    var pth = '/joinPool/' + f(pool.id) +'/name/'+ f(pool.name) + '/address/' + f(pool.address) + '/date/' + f(pool.date) + '/time/' + f(pool.time) + '/dateTime/' + f(pool.dateTime) + '/email/' + f(pool.email) + '/notice/' + f(pool.fireNotice) + "/latenessWindow/" + f(pool.latenessWindow) +"/carpooler/cpname/" + f(cp.name) + '/cpfirst/' + f(cp.first) + '/cplast/' + f(cp.last) + '/cpemail/' + f(cp.email) + '/past_addresses/' + f(JSON.stringify($scope.past_addresses)) + '/max_seats/' + f($scope.max_num_seats) + '/ever_must_drive/' + f($scope.ever_must_drive) + '/ever_organizer/' + f($scope.ever_organizer);
    $log.log(pth);
    // $log.log($window.encodeURIComponent(pth));
    // $location.path($window.encodeURIComponent(pth));
    $location.path(pth);
  };

}]);